import time
from datetime import date, timedelta

from schema import *
import pvpreport
import util
from util import get_new_session
from worker import *


class IntelTool:
    ALL_SHIPS = []

    CAPITAL_GROUP = [30, 547, 485, 659]

    EWAR_TACKLE_MODULE_GROUP = [1441, 52, 1442]

    BLING = ['C-Type', 'X-Type', 'A-Type', 'B-Type', 'C-Type', \
             'Republic Fleet', 'Caldari Navy', 'Dark Blood', 'Sansha', "Shadow Serpentis", 'Dread Guristas',
             "Domination", "Khandid" \
        , "Hakim's", "Mizuro's", "Tobia's", "Gotan's", ]

    def __init__(self, name, alliance_ids=None, corporation_ids=None):
        self.session = get_new_session()
        self.name = name
        self.alliance_ids = alliance_ids
        self.corporation_ids = corporation_ids
        for group in self.session.query(EveGroup.id).filter(EveGroup.category_id == 6).all():
            self.ALL_SHIPS.append(group[0])

    def run(self):
        after = date.today() - timedelta(days=30)

        # Blingy Tackle Report
        mr1 = pvpreport.ModuleReport(get_new_session())
        mr1.alliance_ids = self.alliance_ids
        mr1.corporation_ids = self.corporation_ids
        mr1.groupids = self.EWAR_TACKLE_MODULE_GROUP
        mr1.searchnames = self.BLING
        mr1.kills = True
        mr1.losses = True
        mr1.after = None
        print("Running Blingy Tackle Report...")
        spawn_task(mr1)


        # Capital Pilots 30 Day Profile
        pr1 = pvpreport.ProfileReport(get_new_session())
        pr1.alliance_ids = self.alliance_ids
        pr1.corporation_ids = self.corporation_ids
        pr1.groupids = self.CAPITAL_GROUP
        pr1.kills = True
        pr1.losses = False
        pr1.after = after
        print("Running Capital Pilots 30 Day Profile...")
        spawn_task(pr1)


        # Subcap Activity Kills 30 Days
        ar1 = pvpreport.ActivityReport(get_new_session())
        ar1.alliance_ids = self.alliance_ids
        ar1.corporation_ids = self.corporation_ids
        ar1.groupids = self.CAPITAL_GROUP
        ar1.groupidsinvert = True
        ar1.kills = True
        ar1.after = after
        print("Running Subcaps 30 Day Kills...")
        spawn_task(ar1)


        # Subcap Activity Loss 30 Days
        ar2 = pvpreport.ActivityReport(get_new_session())
        ar2.alliance_ids = self.alliance_ids
        ar2.corporation_ids = self.corporation_ids
        ar2.groupids = self.CAPITAL_GROUP
        ar2.groupidsinvert = True
        ar2.kills = False
        ar2.losses = True
        ar2.after = after
        spawn_task(ar2)


        # Captial Activity Kills 30 Days
        ar3 = pvpreport.ActivityReport(get_new_session())
        ar3.alliance_ids = self.alliance_ids
        ar3.corporation_ids = self.corporation_ids
        ar3.groupids = self.CAPITAL_GROUP
        ar3.groupidsinvert = False
        ar3.kills = True
        ar3.after = after
        print("Running Subcaps 30 Day Losses...")
        spawn_task(ar3)


        # CapvSub Activity Kills 30 Days
        ar4 = pvpreport.ActivityReport(get_new_session())
        ar4.alliance_ids = self.alliance_ids
        ar4.corporation_ids = self.corporation_ids
        ar4.groupids = self.CAPITAL_GROUP
        ar4.groupidsinvert = False
        ar4.againstgroup_ids = self.ALL_SHIPS
        ar4.kills = True
        ar4.after = after
        print("Running CapvSub Activity 30 Days...")
        spawn_task(ar4)

        kr1 = pvpreport.KillMailReport(get_new_session())
        kr1.alliance_ids = self.alliance_ids
        kr1.corporation_ids = self.corporation_ids
        kr1.groupids = self.CAPITAL_GROUP
        kr1.groupidsinvert = False
        kr1.againstgroup_ids = self.ALL_SHIPS
        kr1.after = after
        print("Running CapvSub Killmails 30 Days...")
        spawn_task(kr1)

        # Capital Activity Loss 30 Days
        ar5 = pvpreport.ActivityReport(get_new_session())
        ar5.alliance_ids = self.alliance_ids
        ar5.corporation_ids = self.corporation_ids
        ar5.groupids = self.CAPITAL_GROUP
        ar5.groupidsinvert = False
        ar5.kills = False
        ar5.losses = True
        ar5.after = after
        print("Running Capitals 30 Day Kills...")
        spawn_task(ar5)


        # Gang Report 30 Days
        gr1 = pvpreport.GangSizeReport(get_new_session())
        gr1.alliance_ids = self.alliance_ids
        gr1.corporation_ids = self.corporation_ids
        print("Running Gang Size Report...")
        spawn_task(gr1)

        # Wait for reports to complete
        wait_tasks()

        # Write report results to excel
        util.write_excel("%s_intel_data.xlsx" % (self.name), "Blingy Tackle", mr1.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "Capital Pilots 30 Days", pr1.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "Subcap Kill Activity 30 Days", ar1.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "Subcap Loss Activity 30 Days", ar2.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "Capital Kill Activity 30 Days", ar3.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "CapvSub Activity 30 Days", ar4.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "CapvSub Killmails 30 Days", kr1.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "Capital Loss Activity 30 Days", ar5.arr_result())
        util.write_excel("%s_intel_data.xlsx" % (self.name), "Gang Size 30 Days", gr1.arr_result())
