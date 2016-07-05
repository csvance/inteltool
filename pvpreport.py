from decimal import InvalidOperation

from sqlalchemy.orm import aliased
from sqlalchemy import func, case, desc, or_, not_, and_

from schema import *


class PvPReport:
    def __init__(self, session):
        self.session = session
        self.alliance_ids = None
        self.corporation_ids = None
        self.groupids = None
        self.groupidsinvert = False
        self.after = None
        self.before = None
        self.query = None

    def arr_result(self):
        r_arr = []
        r_arr.append([])
        # add column names
        for column in self.columns:
            r_arr[0].append(column['name'])

        r = 1
        # add row values
        for row in self.results:
            r_arr.append([])
            for item in row:
                r_arr[r].append(item)
            r += 1

        return r_arr

class DestroyedReport(PvPReport):
    def __init__(self,session):
        super(DestroyedReport,self).__init__(session)
        self.region_ids = None
        self.category_ids = None
        self.type_ids = None

    def run(self):

        q = self.session.query(EveType.name,func.sum(Drop.dropped).label('dropped'),\
                               func.sum(Drop.destroyed).label('destroyed'),func.date(KillMail.timestamp).label('date')).\
                                join(Drop,Drop.evetype_id == EveType.id).\
                                join(KillMail, KillMail.id == Drop.killmail_id).\
                                join(SolarSystem, SolarSystem.id == KillMail.solarsystem_id).\
                                join(Region, Region.id == SolarSystem.region_id).\
                                join(EveGroup,EveGroup.id == EveType.group_id).\
                                join(EveCategory,EveCategory.id == EveGroup.category_id)

        if(self.region_ids):
            q = q.filter(Region.id.in_(self.region_ids))

        if(self.type_ids):
            q = q.filter(EveType.id.in_(self.type_ids))

        if(self.category_ids):
            q = q.filter(EveCategory.id.in_(self.category_ids))

        if (self.after):
            q = q.filter(KillMail.timestamp >= self.after)
        if (self.before):
            q = q.filter(KillMail.timestamp <= self.before)

        q = q.group_by(EveType.id,desc('date'))
        q = q.order_by(EveType.id,desc('date'))

        self.query = q
        self.columns = q.column_descriptions
        self.results = q.all()


class ModuleReport(PvPReport):
    def __init__(self, session):
        super(ModuleReport, self).__init__(session)
        self.searchnames = None

    def run(self):

        aq = None
        if (self.kills):
            aq = self.session.query(EveType.name.label("Module")).join(EveGroup, EveGroup.id == EveType.group_id). \
                join(Attacker, Attacker.weapon_id == EveType.id). \
                join(KillMail, KillMail.id == Attacker.killmail_id). \
                add_column(KillMail.id.label("killmail_id")). \
                add_column(KillMail.timestamp.label("datetime")). \
                join(Alliance, Alliance.id == Attacker.alliance_id, isouter=True). \
                join(Corporation, Corporation.id == Attacker.corporation_id). \
                add_column(Alliance.name.label("alliance")).add_column(Corporation.name.label("corporation")). \
                join(Pilot, Pilot.id == Attacker.pilot_id). \
                add_column(Pilot.name.label("Pilot"))

            etship = aliased(EveType)

            aq = aq.join(etship, etship.id == Attacker.ship_id, isouter=True). \
                add_column(etship.name.label("Ship"))

            if (self.searchnames):
                conds = []
                for search in self.searchnames:
                    conds.append(EveType.name.contains(search))
                aq = aq.filter(or_(*conds))

            if (self.groupids != None and not self.groupidsinvert):
                aq = aq.filter(EveGroup.id.in_(self.groupids))
            elif (self.groupids != None and self.groupidsinvert):
                aq = aq.filter(not_(EveGroup.id.in_(self.groupids)))

            saq = self.session.query(Attacker.pilot_id)

            # Attackers is all attackers in the same killmail as another alliance or corporation
            # atk2 is all attackers in an alliance or corporation
            atk2 = aliased(Attacker)

            if (self.alliance_ids and self.corporation_ids):
                saq = saq.filter(
                    and_(atk2.alliance_id.in_(self.alliance_ids), atk2.corporation_id.in_(self.corporation_ids)))
            elif (self.alliance_ids):
                saq = saq.filter(atk2.alliance_id.in_(self.alliance_ids))
            elif (self.corporation_ids):
                saq = saq.filter(atk2.corporation_id.in_(self.corporation_ids))

            saq = saq.filter(Attacker.killmail_id == atk2.killmail_id)

            # Filter the main query using any associated pilots
            aq = aq.filter(Attacker.pilot_id.in_(saq.subquery()))

            if (self.after):
                aq = aq.filter(KillMail.timestamp >= self.after)
            if (self.before):
                aq = aq.filter(KillMail.timestamp <= self.before)

        lq = None
        if (self.losses):
            lq = self.session.query(EveType.name.label("Module")).join(EveGroup, EveGroup.id == EveType.group_id). \
                join(Drop, Drop.evetype_id == EveType.id). \
                join(KillMail, KillMail.id == Drop.killmail_id). \
                add_column(KillMail.id.label("killmail_id")). \
                add_column(KillMail.timestamp.label("datetime")). \
                join(Alliance, Alliance.id == KillMail.alliance_id, isouter=True). \
                join(Corporation, Corporation.id == KillMail.corporation_id). \
                add_column(Alliance.name.label("alliance")).add_column(Corporation.name.label("corporation")). \
                join(Pilot, Pilot.id == KillMail.pilot_id). \
                add_column(Pilot.name.label("Pilot"))

            etship = aliased(EveType)

            lq = lq.join(etship, etship.id == KillMail.ship_id, isouter=True). \
                add_column(etship.name.label("Ship"))

            if (self.searchnames):
                conds = []
                for search in self.searchnames:
                    conds.append(EveType.name.contains(search))
                lq = lq.filter(or_(*conds))

            if (self.groupids != None and not self.groupidsinvert):
                lq = lq.filter(EveGroup.id.in_(self.groupids))
            elif (self.groupids != None and self.groupidsinvert):
                lq = lq.filter(not_(EveGroup.id.in_(self.groupids)))

            if (self.alliance_ids and self.corporation_ids):
                lq = lq.filter(
                    KillMail.corporation_id.in_(self.corporation_ids) or "alliance_id".in_(self.alliance_ids))
            elif (self.corporation_ids):
                lq = lq.filter(KillMail.corporation_id.in_(self.corporation_ids))
            elif (self.alliance_ids):
                lq = lq.filter(KillMail.alliance_id.in_(self.alliance_ids))

            if (self.after):
                lq = lq.filter(KillMail.timestamp >= self.after)
            if (self.before):
                lq = lq.filter(KillMail.timestamp <= self.before)

        query = None
        if (self.kills and self.losses):
            query = aq.union(lq)
        elif (self.kills):
            query = aq
        elif (self.losses):
            query = lq
        else:
            raise Exception("Please select kills, losses, or both")

        query = query.order_by(desc("datetime"))

        self.columns = query.column_descriptions
        self.results = query.all()

        return


class KillMailReport(PvPReport):
    def __init__(self, session):
        super(KillMailReport, self).__init__(session)
        self.kills = True
        self.losses = False
        self.againstgroup_ids = None

    def run(self):

        q = self.session.query(KillMail.id.label('killmail_id'), KillMail.timestamp.label('datetime'), \
                               Alliance.name.label('alliance'), Corporation.name.label('corporation'), \
                               Pilot.name.label('pilot'), EveType.name.label('ship'))

        # Build a subquery to get killmail ids for attackers in corporations and alliances
        sqk = None

        sqk = self.session.query()
        sqk = sqk.add_column(Attacker.killmail_id)
        sqk = sqk.join(EveType, EveType.id == Attacker.ship_id)
        if (self.alliance_ids and self.corporation_ids):
            sqk = sqk.filter(
                _or(Attacker.corporation_id.in_(self.corporation_ids), Attacker.alliance_id.in_(self.alliance_ids)))
        elif (self.alliance_ids):
            sqk = sqk.filter(Attacker.alliance_id.in_(self.alliance_ids))
        elif (self.corporation_ids):
            sqk = sqk.filter(Attacker.corporation_id.in_(self.corporation_ids))
        if (self.groupids != None and not self.groupidsinvert):
            sqk = sqk.join(EveGroup, and_(EveGroup.id == EveType.group_id, EveType.id == Attacker.ship_id),
                           isouter=True). \
                filter(EveGroup.id.in_(self.groupids))
        elif (self.groupids != None and self.groupidsinvert):
            sqk = sqk.join(EveGroup, and_(EveGroup.id == EveType.group_id, EveType.id == Attacker.ship_id),
                           isouter=True). \
                filter(not_(EveGroup.id.in_(self.groupids)))

        q = q.filter(KillMail.id.in_(sqk.subquery())). \
            filter(EveType.id == KillMail.ship_id). \
            filter(EveGroup.id == EveType.group_id). \
            filter(Pilot.id == KillMail.pilot_id). \
            filter(KillMail.alliance_id == Alliance.id). \
            filter(KillMail.corporation_id == Corporation.id)

        # Search for a specific target type
        if (self.againstgroup_ids and self.kills):
            q = q.filter(EveGroup.id.in_(self.againstgroup_ids))

        if (self.after):
            q = q.filter(KillMail.timestamp >= self.after)
        if (self.before):
            q = q.filter(KillMail.timestamp <= self.before)

        self.columns = q.column_descriptions
        self.results = q.all()

        return


class ProfileReport(PvPReport):
    def __init__(self, session):
        super(ProfileReport, self).__init__(session)

    def run(self):

        q = self.session.query(Alliance.name.label('alliance'), Corporation.name.label('corporation'), \
                               Pilot.name.label('pilot'), EveType.name.label('ship'),
                               func.count(KillMail.id).label('kills'))

        if (self.groupids != None and not self.groupidsinvert):
            q = q.filter(EveGroup.id.in_(self.groupids))
        elif (self.groupids != None and self.groupidsinvert):
            q = q.filter(not_(EveGroup.id.in_(self.groupids)))

        q = q.filter(EveGroup.id == EveType.group_id). \
            filter(Attacker.ship_id == EveType.id). \
            filter(Attacker.killmail_id == KillMail.id). \
            filter(Attacker.alliance_id == Alliance.id). \
            filter(Attacker.pilot_id == Pilot.id). \
            filter(Attacker.corporation_id == Corporation.id)

        # Build subquery to get all pilots on target killmails
        atk2 = aliased(Attacker)

        sq = self.session.query(Attacker.pilot_id). \
            join(atk2, atk2.killmail_id == Attacker.killmail_id)

        if (self.alliance_ids and self.corporation_ids):
            sq = sq.filter(atk2.corporation_id.in_(self.corporation_ids) or atk2.alliance_id.in_(self.alliance_ids))
        elif (self.corporation_ids):
            sq = sq.filter(atk2.corporation_id.in_(self.corporation_ids))
        elif (self.alliance_ids):
            sq = sq.filter(atk2.alliance_id.in_(self.alliance_ids))
        sq = sq.group_by(Attacker.pilot_id)

        if (self.after):
            q = q.filter(KillMail.timestamp >= self.after)
        if (self.before):
            q = q.filter(KillMail.timestamp <= self.before)

        q = q.filter(Pilot.id.in_(sq.subquery())). \
            group_by(Pilot.name). \
            order_by(func.count(KillMail.id).desc())

        self.columns = q.column_descriptions
        self.results = q.all()
        return


class ActivityReport(PvPReport):
    def __init__(self, session):
        super(ActivityReport, self).__init__(session)
        self.kills = True
        self.losses = False
        self.againstgroup_ids = None

    def column_name(self, c_name):
        if (c_name == 1):
            return 'Sunday'
        elif (c_name == 2):
            return 'Monday'
        elif (c_name == 3):
            return 'Tuesday'
        elif (c_name == 4):
            return 'Wednesday'
        elif (c_name == 5):
            return 'Thursday'
        elif (c_name == 6):
            return 'Friday'
        elif (c_name == 7):
            return 'Saturday'
        elif (c_name == 'dow'):
            return ''

        return c_name

    def arr_result(self):
        result = super(ActivityReport, self).arr_result()
        # Translate Column Names
        r = 0
        for row in result:
            result[r][0] = self.column_name(result[r][0])
            r += 1

        return result

    def run(self):

        q = self.session.query()

        # Add day of week
        q = q.add_column(func.dayofweek(KillMail.timestamp).label('dow'))

        # Add an hour for each column.
        for h in range(0, 24):
            q = q.add_column(func.sum(case([(func.hour(KillMail.timestamp) == h, 1)], else_=0)).label("%02i" % (h)))

        # Build a subquery to get killmail ids for attackers or victims in corporations and alliances
        sqk = None
        sql = None
        if (self.kills):
            sqk = self.session.query()
            sqk = sqk.add_column(Attacker.killmail_id)
            sqk = sqk.join(EveType, EveType.id == Attacker.ship_id)
            if (self.alliance_ids and self.corporation_ids):
                sqk = sqk.filter(
                    _or(Attacker.corporation_id.in_(self.corporation_ids), Attacker.alliance_id.in_(self.alliance_ids)))
            elif (self.alliance_ids):
                sqk = sqk.filter(Attacker.alliance_id.in_(self.alliance_ids))
            elif (self.corporation_ids):
                sqk = sqk.filter(Attacker.corporation_id.in_(self.corporation_ids))
            if (self.groupids != None and not self.groupidsinvert):
                sqk = sqk.join(EveGroup, and_(EveGroup.id == EveType.group_id, EveType.id == Attacker.ship_id),
                               isouter=True). \
                    filter(EveGroup.id.in_(self.groupids))
            elif (self.groupids != None and self.groupidsinvert):
                sqk = sqk.join(EveGroup, and_(EveGroup.id == EveType.group_id, EveType.id == Attacker.ship_id),
                               isouter=True). \
                    filter(not_(EveGroup.id.in_(self.groupids)))

        if (self.losses):
            sql = self.session.query()
            km2 = aliased(KillMail)
            sql = sql.add_column(km2.id)
            sql = sql.join(EveType, EveType.id == km2.ship_id)
            if (self.alliance_ids and self.corporation_ids):
                sql = sql.filter(
                    _or(km2.corporation_id.in_(self.corporation_ids), km2.alliance_id.in_(self.alliance_ids)))
            elif (self.alliance_ids):
                sql = sql.filter(km2.alliance_id.in_(self.alliance_ids))
            elif (self.corporation_ids):
                sql = sql.filter(km2.corporation_id.in_(self.corporation_ids))
            if (self.groupids != None and not self.groupidsinvert):
                sql = sql.join(EveGroup, and_(EveGroup.id == EveType.group_id, EveType.id == km2.ship_id),
                               isouter=True). \
                    filter(EveGroup.id.in_(self.groupids))
            elif (self.groupids != None and self.groupidsinvert):
                sql = sql.join(EveGroup, and_(EveGroup.id == EveType.group_id, EveType.id == km2.ship_id),
                               isouter=True). \
                    filter(not_(EveGroup.id.in_(self.groupids)))

        if (self.kills and self.losses):
            q = q.filter(or_(KillMail.id.in_(sql.subquery()), KillMail.id.in_(sqk.subquery())))
        elif (self.kills):
            q = q.filter(KillMail.id.in_(sqk.subquery()))
        elif (self.losses):
            q = q.filter(KillMail.id.in_(sql.subquery()))
        else:
            raise Exception("Please select kills, losses, or both")

        # Search for a specific target type
        if (self.againstgroup_ids and self.kills and not self.losses):
            et2 = aliased(EveType)
            eg2 = aliased(EveGroup)
            q = q.join(et2, et2.id == KillMail.ship_id). \
                join(eg2, eg2.id == et2.group_id). \
                filter(eg2.id.in_(self.againstgroup_ids))

        if (self.after):
            q = q.filter(KillMail.timestamp >= self.after)
        if (self.before):
            q = q.filter(KillMail.timestamp <= self.before)

        q = q.group_by('dow'). \
            order_by(desc('dow'))

        self.columns = q.column_descriptions
        self.results = q.all()

        return


class GangSizeReport(ActivityReport):
    def __init__(self, session):
        super(GangSizeReport, self).__init__(session)
        self.session = session

    def arr_result(self):
        return self.final_result

    def _arr_result(self):
        result = super(ActivityReport, self).arr_result()

        # Remove extra column that we are forced to use and fix naming
        r = 0
        for row in result:
            result[r].pop(0)
            result[r][0] = self.column_name(result[r][0])
            r += 1

        return result

    def run(self):

        q = self.session.query(Attacker)


        # Build a subquery to get killmail ids for attackers or victims in corporations and alliances
        sqk = None

        sqk = self.session.query()
        sqk = sqk.add_column(Attacker.id)
        if (self.alliance_ids and self.corporation_ids):
            sqk = sqk.filter(
                _or(Attacker.corporation_id.in_(self.corporation_ids), Attacker.alliance_id.in_(self.alliance_ids)))
        elif (self.alliance_ids):
            sqk = sqk.filter(Attacker.alliance_id.in_(self.alliance_ids))
        elif (self.corporation_ids):
            sqk = sqk.filter(Attacker.corporation_id.in_(self.corporation_ids))
        if (self.groupids != None and not self.groupidsinvert):
            sqk = sqk.join(EveGroup, and_(EveType.id == Attacker.ship_id, EveGroup.id == EveType.group_id),
                           isouter=True). \
                filter(EveGroup.id.in_(self.groupids))
        elif (self.groupids != None and self.groupidsinvert):
            sqk = sqk.join(EveGroup, and_(EveType.id == Attacker.ship_id, EveGroup.id == EveType.group_id),
                           isouter=True). \
                filter(EveGroup.id.in_(self.groupids))

        # Filter by attackers and left outer join killmails
        q = q.filter(Attacker.id.in_(sqk.subquery())). \
            join(KillMail, KillMail.id == Attacker.killmail_id, isouter=True)

        # Add day of week
        q = q.add_column(func.dayofweek(KillMail.timestamp).label('dow')).group_by('dow')

        # Add an hour for each column.
        for h in range(0, 24):
            q = q.add_column((func.sum(case([(func.hour(KillMail.timestamp) == h, 1)], else_=0))).label("%02i" % (h)))

        if (self.after):
            q = q.filter(KillMail.timestamp >= self.after)
        if (self.before):
            q = q.filter(KillMail.timestamp <= self.before)

        q = q.order_by(desc('dow'))

        self.columns = q.column_descriptions
        self.results = q.all()

        attackers_per_hour = self._arr_result()


        # We need to get the number of kills per hour accross 7 days
        ar = ActivityReport(self.session)

        ar.alliance_ids = self.alliance_ids
        ar.corporation_ids = self.corporation_ids
        ar.groupids = self.groupids
        ar.groupidsinvert = self.groupidsinvert
        ar.after = self.after
        ar.before = self.before
        ar.kills = True
        ar.losses = False
        ar.run()

        kills_per_hour = ar.arr_result()

        final_result = []

        # Create the final array and cross divide between the two arrays
        r = 0
        while (r < len(attackers_per_hour)):
            final_result.append([])
            c = 0
            while (c < len(attackers_per_hour[r])):
                # We can't divide on the header
                if (r == 0 or c == 0):
                    final_result[r].append(attackers_per_hour[r][c])
                else:
                    try:
                        final_result[r].append(attackers_per_hour[r][c] / kills_per_hour[r][c])
                    except (ZeroDivisionError, InvalidOperation) as e:
                        final_result[r].append(0)
                c += 1
            r += 1

        self.final_result = final_result
