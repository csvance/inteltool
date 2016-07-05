import csv

import yaml

from schema import *


def import_groupids(session, file):
    def insert_group(g):
        if (session.query(EveGroup.id).filter(EveGroup.id == g).count() == 0):

            iconID = None
            try:
                iconID = icon_id = y[g]['iconID']
            except KeyError:
                pass

            session.add(EveGroup(id=g, name=y[g]['name']['en'], anchorable=y[g]['anchorable'], \
                                 anchored=y[g]['anchored'], category_id=y[g]['categoryID'], \
                                 fittable_non_singleton=y[g]['fittableNonSingleton'], \
                                 published=y[g]['published'], use_base_price=y[g]['useBasePrice'], icon_id=iconID))

    data = open(file, 'r', encoding='utf-8').read()
    y = yaml.load(data)

    for key in y:
        insert_group(key)

    session.commit()


def import_categoryids(session, file):
    def insert_category(c):
        if (session.query(EveCategory.id).filter(EveCategory.id == c).count() == 0):
            session.add(EveCategory(id=c, name=y[c]['name']['en'], published=y[c]['published']))

    data = open(file, 'r', encoding='utf-8').read()
    y = yaml.load(data)

    for key in y:
        insert_category(key)

    session.commit()


def import_typeids(session, file):
    def insert_type(t):
        if (session.query(EveType).filter(EveType.id == t).count() == 0):

            name = None
            try:
                name = y[t]['name']['en']
            except KeyError:
                print("No name for item %d: %s" % (t, y[t]))

            radius = None
            try:
                radius = icon_id = y[t]['radius']
            except KeyError:
                pass

            volume = None
            try:
                volume = icon_id = y[t]['volume']
            except KeyError:
                pass

            capacity = None
            try:
                capacity = icon_id = y[t]['capacity']
            except KeyError:
                pass

            mass = None
            try:
                mass = icon_id = y[t]['mass']
            except KeyError:
                pass

            raceID = None
            try:
                raceID = icon_id = y[t]['raceID']
            except KeyError:
                pass

            sofFactionName = None
            try:
                sofFactionName = icon_id = y[t]['sofFactionName']
            except KeyError:
                pass

            basePrice = None
            try:
                basePrice = icon_id = y[t]['basePrice']
            except KeyError:
                pass

            marketGroupID = None
            try:
                marketGroupID = icon_id = y[t]['marketGroupID']
            except KeyError:
                pass

            graphicID = None
            try:
                graphicID = icon_id = y[t]['graphicID']
            except KeyError:
                pass

            soundID = None
            try:
                soundID = icon_id = y[t]['soundID']
            except KeyError:
                pass

            session.add(EveType(id=t, group_id=y[t]['groupID'], name=name, \
                                published=y[t]['published'], portion_size=y[t]['portionSize'], radius=radius,
                                volume=volume, \
                                capacity=capacity, mass=mass, race_id=raceID, sof_faction_name=sofFactionName, \
                                base_price=basePrice, marketgroup_id=marketGroupID, graphic_id=graphicID, \
                                sound_id=soundID))
            session.commit()

    data = open(file, 'r', encoding='utf-8').read()
    y = yaml.load(data)

    for key in y:
        insert_type(key)
    session.commit()


def import_systems(session, file):
    def clean(s):
        return s.replace("'", "")

    def get_system_assoc(system):
        s = {}
        s['solarsystem_id'] = int(system[0])
        s['region_id'] = int(system[1])
        s['region_name'] = clean(system[2])
        s['solarsystem_name'] = clean(system[3])
        s['security'] = float(system[4])
        s['x'] = int(system[5])
        s['y'] = int(system[6])
        s['z'] = int(system[7])
        s['flat_x'] = int(system[8])
        s['flat_y'] = int(system[9])
        s['dotlan_x'] = int(system[10])
        s['dotlan_y'] = int(system[11])
        if (int(system[12])):
            s['has_station'] = True
        else:
            s['has_station'] = False
        return s


def import_systems(session, file):
    def insert_system(row):
        if (session.query(SolarSystem.id).filter(SolarSystem.id == row[2]).count() == 0):
            session.add(SolarSystem(id=row[2], constellation_id=row[1], name=row[3], \
                                    region_id=row[0], security=row[21], x=row[4], y=row[5], \
                                    z=row[6]))
        else:
            session.query(SolarSystem).filter(SolarSystem.id == row[2]).first().constellation_id = row[1]

    with open(file, 'r') as csvfile:
        systemreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in systemreader:
            insert_system(row)
        session.commit()


def import_regions(session, file):
    def insert_region(row):
        if (session.query(Region.id).filter(Region.id == row[0]).count() == 0):
            session.add(Region(id=row[0], name=row[1]))

    with open(file, 'r') as csvfile:
        regionreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in regionreader:
            insert_region(row)
        session.commit()


def import_constellations(session, file):
    def insert_constellation(row):
        if (session.query(Constellation.id).filter(Constellation.id == row[1]).count() == 0):
            session.add(Constellation(id=row[1], name=row[2], region_id=row[0]))

    with open(file, 'r') as csvfile:
        constellationreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in constellationreader:
            insert_constellation(row)
        session.commit()
