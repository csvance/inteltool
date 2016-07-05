from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
from pylab import *

from scraper import *
import pvpreport


from inteltool import IntelTool

session = get_new_session()

def run_inteltool():
    it = IntelTool("reports/some_alliance", alliance_ids=[123456789]).run()

def run_scraper():
    Scraper().run()

def loss_history_plot_drop(evetype_ids,region_ids,index):

    after = date.today() - timedelta(days=30)
    #Drop Report
    dr1 = pvpreport.DestroyedReport(get_new_session())
    dr1.region_ids = [int(region_ids)]
    dr1.type_ids = evetype_ids
    dr1.category_ids = None
    dr1.after = after
    dr1.run()

    destroyed = []
    dropped = []
    timestamp = []

    result = dr1.arr_result()
    for row in result[1:]:
        dropped.append(int(row[1]))
        destroyed.append(int(row[2]))
        timestamp.append(row[3])

    fig, ax = plt.subplots()

    ax.plot(timestamp,dropped,label='dropped')
    ax.plot(timestamp,destroyed,label='destroyed')
    legend = ax.legend(loc='upper center', shadow=True)
    plt.title( str(index+1) + ": " + result[1:][0][0])
    plt.ylabel('modules')

    #plt.show()
    savefig("plots/moduleloss/%d_%s.png" %  (index+1,result[1:][0][0]), bbox_inches='tight')
    plt.clf()

def top_100_modules_region(region_ids):
    i = 0
    query = """
    SELECT evetypes.id, evetypes.name AS evetypes_name,
    sum(drops.destroyed) AS destroyedcount,
    sum(drops.dropped) AS droppedcount, sum(drops.destroyed)/sum(drops.dropped) as needratio
    FROM drops, evetypes,killmails, solarsystems,regions,evegroups,evecategories
    where
    killmails.id = drops.killmail_id AND
    solarsystems.id = killmails.solarsystem_id AND
    regions.id = solarsystems.region_id AND
    evegroups.id = evetypes.group_id AND
    evecategories.id = evegroups.category_id AND
    drops.evetype_id = evetypes.id AND
    regions.id IN (%s) and
    evecategories.name = 'Module' and
    not INSTR(evegroups.name,'Rig')
    GROUP BY evetypes.id
    ORDER BY destroyedcount desc, needratio limit 100""" % (region_ids)
    result = engine.execute(query)
    for row in result:
        loss_history_plot_drop([row[0]],region_ids,i)
        i+=1

run_scraper()
top_100_modules_region("10000048")
run_inteltool()





