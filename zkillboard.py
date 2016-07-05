import gzip
import string
import json
from urllib import request
from urllib.error import HTTPError
import os.path
import time
from os import listdir
from os.path import isfile, join
import datetime

from schema import *
from util import *


class CachedHTTPRequest():
    def __init__(self, cachepath="cache", expires=79800.0):
        self.cachepath = cachepath
        self.expires = expires

    def format_filename(self, s):
        s = s.replace("/", "_")
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in s if c in valid_chars)
        filename = filename.replace(' ', '_')
        return filename

    def get_cachepath(self):
        return "%s/%s" % (self.cachepath, self.format_filename(self.url))

    def get_cache(self):
        try:
            cache_time = os.path.getmtime(self.get_cachepath())
        except FileNotFoundError:
            return None

        cache_time = os.path.getmtime(self.get_cachepath())
        expire = (cache_time + self.expires) - time.time()

        if (expire <= 0.0):
            return None

        return {"data": open(self.get_cachepath(), 'rb').read(), "expire": int(expire)}

    def set_cache(self, data):
        open(self.get_cachepath(), 'wb').write(data)

    def http_request(self):
        print("Requesting %s" % (self.url))
        data = None
        r = request.Request(self.url)
        r.add_header("User-Agent", "Python 3.4 urllib - %s" % (self.userid))
        r.add_header("Accept-encoding", "gzip")

        response = request.urlopen(r)

        headers = response.info()
        retry = None
        try:
            retry = headers['Retry-After']
            if (retry != None):
                raise Exception("Retry-After: %s" % (retry))
        except KeyError:
            pass

        if response.info().get('Content-Encoding') == 'gzip':
            buf = response
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
        else:
            data = response.read()

        return data

    def get_request(self):
        data = {}
        cache = self.get_cache()

        if (cache == None):
            data['wascached'] = False
            data['response'] = self.http_request()
            self.set_cache(data['response'])
        else:
            data['wascached'] = True
            data['response'] = cache['data']
            expire = cache['expire']
            print("Note: Using cached request for url %s (Expiration: %s seconds.)" % (self.url, expire))

        return data


class zKillboardRequest(CachedHTTPRequest):
    BASE_URL = " http://zkillboard.com/api"

    def __init__(self, userid, entityid=None, entitytype=None, killloss=None, beforeid=None, afterid=None, order=None,
                 expires=79800.0):
        super(zKillboardRequest, self).__init__(expires=expires)
        self.userid = userid
        self.entitytype = entitytype
        self.entityid = entityid
        self.killloss = killloss
        self.beforeid = beforeid
        self.afterid = afterid
        self.order = order
        self.build_url()

    def build_url(self):
        url = self.BASE_URL
        if (self.killloss != None):
            url = "%s/%s" % (url, self.killloss)
        if (self.entityid != None):
            url = "%s/%sID/%s" % (url, self.entitytype, self.entityid)
        if (self.beforeid != None):
            url = "%s/beforeKillID/%s" % (url, self.beforeid)
        elif (self.afterid != None):
            url = "%s/afterKillID/%s" % (url, self.afterid)
        if (self.order):
            url = "%s/orderDirection/%s" % (url, self.order)

        url = "%s/" % (url)

        self.url = url

    def get_kills(self):
        data = self.get_request()
        data['killmails'] = json.loads(data['response'].decode('utf-8'))
        return data


class zKillboardScraper():
    MAX_RESPONSE_KILLMAILS = 200

    def __init__(self, session, userid, killloss=None, entitytype=None, entityid=None, afterid=None, requestdelay=15,
                 expires=3600.0):
        self.session = session
        self.userid = userid
        self.killloss = killloss
        self.entitytype = entitytype
        self.entityid = entityid
        self.afterid = afterid
        self.requestdelay = requestdelay
        self.expires = expires

    def insert_corporation(self, id, name):
        if (self.session.query(Corporation.id).filter(Corporation.id == id).count() != 0):
            return
        self.session.add(Corporation(id=id, name=name))

    def insert_alliance(self, id, name):
        if (self.session.query(Alliance.id).filter(Alliance.id == id).count() != 0):
            return
        self.session.add(Alliance(id=id, name=name))

    def insert_pilot(self, id, name):
        if (self.session.query(Pilot.id).filter(Pilot.id == id).count() != 0):
            return
        self.session.add(Pilot(id=id, name=name))

    def insert_drop(self, killmail_id, typeid, flag, dropped, destroyed, singleton):
        if (singleton):
            singleton = True
        else:
            singleton = False

        self.session.add(
            Drop(killmail_id=killmail_id, evetype_id=typeid, dropped=dropped, destroyed=destroyed, singleton=singleton))

    def insert_killmail(self, km):

        if (self.session.query(KillMail.id).filter(KillMail.id == km['killID']).count() != 0):
            return

        # Null allowable
        alliance_id = zero2none(km['victim']['allianceID'])
        pilot_id = zero2none(km['victim']['characterID'])

        if (alliance_id):
            self.insert_alliance(km['victim']['allianceID'], km['victim']['allianceName'])

        self.insert_corporation(km['victim']['corporationID'], km['victim']['corporationName'])

        if (pilot_id):
            self.insert_pilot(km['victim']['characterID'], km['victim']['characterName'])

        killmailtime = datetime.datetime.strptime(km['killTime'], '%Y-%m-%d %H:%M:%S')

        self.session.add(KillMail(id=km['killID'], pilot_id=pilot_id, \
                                  solarsystem_id=km['solarSystemID'], corporation_id=km['victim']['corporationID'], \
                                  alliance_id=alliance_id, timestamp=killmailtime, ship_id=km['victim']['shipTypeID']))
        self.session.commit()

        a = 0
        for attacker in km['attackers']:
            # These are allowed to be null
            alliance_id = zero2none(attacker['allianceID'])
            corporation_id = zero2none(attacker['corporationID'])
            pilot_id = zero2none(attacker['characterID'])
            weapon_id = zero2none(attacker['weaponTypeID'])
            ship_id = zero2none(attacker['shipTypeID'])

            if (alliance_id):
                self.insert_alliance(attacker['allianceID'], attacker['allianceName'])
            if (corporation_id):
                self.insert_corporation(attacker['corporationID'], attacker['corporationName'])
            if (pilot_id):
                self.insert_pilot(attacker['characterID'], attacker['characterName'])

            self.session.add(Attacker(pilot_id=pilot_id, killmail_id=km['killID'], \
                                      corporation_id=corporation_id, alliance_id=alliance_id, \
                                      ship_id=ship_id, weapon_id=weapon_id, \
                                      damage=attacker['damageDone'], killingblow=attacker['finalBlow']))
            a += 1

        for item in km['items']:
            if (self.session.query(EveType.id).filter(EveType.id == item['typeID']).count() == 0):
                print("Killmail ID: %d is a DUST514 kill with drop evetypeid: %d. Removing from database." % (
                km['killID'], item['typeID']))
                self.session.rollback()
                self.session.query(Pilot).filter(id == km['victim']['characterID']).delete()
                self.session.query(Alliance).filter(id == km['victim']['allianceID']).delete()
                self.session.query(Corporation).filter(id == km['victim']['corporationID']).delete()
                self.session.query(KillMail).filter(KillMail.id == km['killID']).delete()
                return
            self.insert_drop(km['killID'], item['typeID'], item['flag'], item['qtyDropped'], item['qtyDestroyed'],
                             item['singleton'])

    def scrape_file(self, file):
        data = open(file, 'rb').read()
        data = data.decode('utf-8')
        j = json.loads(data)
        for kill in j:
            self.insert_killmail(kill)

    def scrape_dir(self, dir):
        onlyfiles = [join(dir, f) for f in listdir(dir) if isfile(join(dir, f))]
        print(onlyfiles)
        for file in onlyfiles:
            self.scrape_file(file)

    def getafterid(self):
        q = self.session.query(ScraperStatus.last_id).filter(ScraperStatus.source_name == 'zKillboardScraper')

        row = q.first()

        if (row != None):
            return row[0]
        else:
            return None

    def setafterid(self, id):
        currentafterid = self.getafterid()

        if (id == currentafterid):
            return

        if (currentafterid == None):
            self.session.add(
                ScraperStatus(source_name='zKillboardScraper', last_scrape=datetime.datetime.utcnow(), last_id=id))
        else:
            status = self.session.query(ScraperStatus).filter(ScraperStatus.source_name == 'zKillboardScraper').first()
            status.last_id = id
            self.session.commit()

    def run(self):

        if (self.afterid == None):
            self.afterid = self.getafterid()

        while (True):

            # Get kills after the afterid
            z = zKillboardRequest(self.userid, killloss=self.killloss, entitytype=self.entitytype,
                                  entityid=self.entityid, afterid=self.afterid, expires=self.expires, order='asc')

            r = z.get_kills()
            killmails = r['killmails']
            wascached = r['wascached']

            print("Got %d killmails to process" % (len(killmails)))

            for killmail in killmails:
                self.insert_killmail(killmail)
            self.session.commit()

            oldafterid = self.afterid
            newafterid = killmails[-1]['killID']

            if (len(killmails) < self.MAX_RESPONSE_KILLMAILS or oldafterid == newafterid):
                self.setafterid(newafterid)
                print("All done!")
                break

            self.afterid = newafterid
            self.setafterid(newafterid)

            print("Next after killid to request: %d" % (self.afterid))
            if (not wascached and self.requestdelay):
                print("Sleeping %d seconds..." % (self.requestdelay))
                time.sleep(self.requestdelay)
