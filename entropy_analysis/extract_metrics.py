from __future__ import division
import csv
import MySQLdb
from numpy import median, percentile
from mysql_bug_interface import Mysqlbug

# build bug list
def buildBugList():
    inputDict = dict()
    entropyList, frequencyList = list(), list()
    for row in csvfile:
        inputDict[row[0]] = (float(row[1]), int(row[2]), float(row[4]))
        entropyList.append(float(row[1]))
        frequencyList.append(int(row[2]))
    '''#    bugList.append((row[0], float(row[1]), float(row[2])))
    splitList = [list(t) for t in zip(*bugList)]'''
    #entropy_cutoff = median(entropyList)
    #frequency_cutoff = median(frequencyList)
    entropy_cutoff = percentile(entropyList, sensitivity_level)
    frequency_cutoff = percentile(frequencyList, sensitivity_level)
    return (inputDict, entropy_cutoff, frequency_cutoff)

# determine whether a bug report has invalid status
def hasInvalid(bug):
    r = bug['resolution']
    if(r == 'INVALID' or r == 'WONTFIX' or r == 'WORKSFORME' or r == 'DUPLICATE'):
        return 'YES'
    else:
        return 'NO'

def isClosed(bug):
    r = bug['status']
    if(r == 'VERIFIED' or r == 'RESOLVED'):
        return 1
    else:
        return 0

# count patch number of a bug
def patchCount(bugID):
    cursor.execute('SELECT ispatch FROM attachments WHERE bug_id = ' + bugID)
    results = cursor.fetchall()
    patch_cnt = 0
    for r in results:
        if(r[0] == 1):
            patch_cnt += 1
    return patch_cnt

def developerCount(bugID):
    cursor.execute('SELECT COUNT(DISTINCT who) FROM bugs_activity where bug_id = ' + bugID)
    results = cursor.fetchall()
    return results[0][0]

# extract metrics from bug database
def extractMetrics(mysqlbugdb, inputDict):
    print 'Extracting metrics ...'
    bugDict = dict()
    for bugID in inputDict:
        bug = mysqlbugdb.getBug(bugID)
        if(bug):
            metricDict = {}
            metricDict['create_time'] = bug['create_time']
            metricDict['title'] = bug['sign']
            metricDict['platform'] = None
            metricDict['severity'] = bug['severity']
            metricDict['priority'] = bug['priority']
            metricDict['last_modified'] = bug['last_modified']
            metricDict['reporter'] = None
            metricDict['assignee'] = None
            metricDict['component'] = None            
            # cc_count
            metricDict['cc_count'] = bug['cc_count']
            # comment
            metricDict['comment'] = bug['comment_count']
            # attachment
            metricDict['patch_count'] = 0
            # invalid_status
            metricDict['invalid'] = hasInvalid(bug)
            # reopened_count
            metricDict['reopened_count'] = None
            # developer_count
            metricDict['developer_count'] = None
            # is closed
            metricDict['is_closed'] = isClosed(bug)
            # uptime
            metricDict['uptime'] = inputDict[bugID][2]
            # fixed time (if not fixed, fixed_time = -1)
            metricDict['fixing_time'] = computeFixingTime(bug)
            componentOfBug(bugID)
            # bug triaging time
            metricDict['triaging_time'] = computeFixingTime(bug)
            # Add bugID/metrics to the bug dict
            bugDict[bugID] = metricDict
        else:
            print bugID
    return bugDict

# format and output the time by hour, weekday, monthday, month and yearday
def formatDate(tm): 
    hour = int(tm.strftime('%H'))
    week_day = tm.strftime('%a')
    month_day = int(tm.strftime('%d'))
    month = tm.strftime('%b')
    year_day = int(tm.strftime('%j'))
    return (hour, week_day, month_day, month, year_day)

# compute experience for reporters and assignees
def computeExperience(userDict, thisUser):
    if(thisUser in userDict):
        currentExp = userDict[thisUser] + 1
        userDict[thisUser] = currentExp
        return currentExp
    else:
        userDict[thisUser] = 1
        return 1

# compute the fixing time
def computeFixingTime(bug):
    if(bug['status'] == 'RESOLVED'):
        create_time = bug['create_time']
        fixed_time = bug['last_modified']
        return round((fixed_time - create_time).total_seconds(), 2)
    return -1

# return the component of a bug
def componentOfBug(bugID):
    # cursor.execute('SELECT name FROM products WHERE id = (SELECT product_id FROM bugs WHERE bug_id = ' + bugID + ')')
    # results = cursor.fetchall()
    # #if(results[0][0] != 'Core'):
    # #print 'product', results[0][0]
    # cursor.execute('SELECT name FROM components WHERE id = (SELECT component_id FROM bugs WHERE bug_id = ' + bugID + ')')
    # results = cursor.fetchall()
    # #print 'component', results[0][0]
    component_set.add('')#results[0][0])
    return

# triaging duration
def triagingDuration(bugID, cursor, opened_time):
    cursor.execute('SELECT added, removed, bug_when FROM bugs_activity WHERE bug_id = ' + bugID + ' ORDER BY bug_when')
    results = cursor.fetchall()
    for row in results:
        if('assign' in row[0].lower()):
            return round((row[2] - opened_time).total_seconds(), 2)
        elif('assign' in row[1].lower()):
            return round((row[2] - opened_time).total_seconds(), 2)
    return '-1'

# decide one of the four regions for bugs 
def decideRegion(bugID, inputDict):
    thisEntropy = inputDict[bugID][0]
    thisFrequency = inputDict[bugID][1]
    if(thisEntropy > entropy_cutoff):
        if(thisFrequency > frequency_cutoff):
            return 'high'
    #return 'other'
        else:
            return 'moderate'
    else:
        if(thisFrequency > frequency_cutoff):
            return 'skewed'
        else:
            return 'isolated'

# analyse and output metrics into a csv file
def outputMetrics(bugDict, inputDict):
    print 'Outputing metrics ...'
    reporterDict, assigneeDict = dict(), dict()
    if(sensitivity_level == 50):
        csv_writer = csv.writer(open('entropy_analysis/bugs/' + product + '_metrics_' + criteria + '.csv', 'wb'))
    else:
        csv_writer = csv.writer(open('entropy_analysis/bugs/' + product + '_' + str(sensitivity_level) + '.csv', 'wb'))
    csv_writer.writerow(['bugID', 'hour', 'week_day', 'month_day', 'month', 'year_day', 'component', \
                        'title_size', 'platform', 'severity', 'priority', 'cc_count', 'comment_size', \
                        'invalid_status', 'is_closed', 'patch_count', 'fixing_time', 'reopened_count', 'triaging_time',\
                        'uptime', 'developer_count', 'reporter_exp', 'assignee_exp', 'region'])
    sortedList = sorted(bugDict.keys())
    for bugID in sortedList:
        metricDict = bugDict[bugID]
        create_time = metricDict['create_time']
        last_modified = metricDict['last_modified']
        title_size = len(metricDict['title'].split())
        platform = metricDict['platform']
        severity = metricDict['severity']
        priority = metricDict['priority']
        cc_count = metricDict['cc_count']
        component = metricDict['component']
        comment_size = metricDict['comment']
        invalid_status = metricDict['invalid']
        is_closed = metricDict['is_closed']
        uptime = metricDict['uptime']
        patch_count = metricDict['patch_count']
        reopened_count = metricDict['reopened_count']
        triaging_time = metricDict['triaging_time']
        developer_count = metricDict['developer_count']
        reporter = metricDict['reporter']
        assignee = metricDict['assignee']
        (hour, week_day, month_day, month, year_day) = formatDate(create_time)
        fixing_time = metricDict['fixing_time']             
        reporter_exp = computeExperience(reporterDict, reporter)
        assignee_exp = computeExperience(assigneeDict, assignee)
        region = decideRegion(bugID, inputDict)
        #if(region == 'high' or region == 'isolated'):
        csv_writer.writerow([bugID, hour, week_day, month_day, month, year_day, component, \
                            title_size, platform, severity, priority, cc_count, comment_size, \
                            invalid_status, is_closed, patch_count, fixing_time, reopened_count, triaging_time,\
                            uptime, developer_count, reporter_exp, assignee_exp, region])
    return

if(__name__ == '__main__'):
    component_set = set()
    product = 'libreoffice'
    criteria = 'machine'
    sensitivity_level = 50

    csvfile = csv.reader(open('entropy_analysis/bugs/' + product + '_entropy_' + criteria + '.csv', 'rb'))
    next(csvfile, None)
    mysqlbugdb = Mysqlbug()
    (inputDict, entropy_cutoff, frequency_cutoff) = buildBugList()

    bugDict = extractMetrics(mysqlbugdb, inputDict)
    outputMetrics(bugDict, inputDict)
    
    comp_list = sorted(list(component_set))
    for c in comp_list:
        print c