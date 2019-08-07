import json
import time
from zowerun import run

class ZoweUser:
    pass

def getDefaultZosmfUser(issuesErrorMessages = True):
    zoweUser = ZoweUser()
    result = run("zowe profiles list zosmf --sc --rfj", issuesErrorMessages)
    if result.stdout:
        zosmfProfile = json.loads(result.stdout)
        zoweUser.user = zosmfProfile['data'][0]['profile']['user'].upper()
        zoweUser.host = zosmfProfile['data'][0]['profile']['host']
        return zoweUser
    else:
        return ''

def createPDS(pdsName, issuesErrorMessages = True):
    result = run("zowe files create classic " + pdsName, issuesErrorMessages)
    if result.stdout:
        return True
    else:
        return False

def deletePDS(pdsName, issuesErrorMessages = True):
    result = run("zowe files delete ds " + pdsName + " -f", issuesErrorMessages)
    if result.stdout:
        return True
    else:
        return False 

def downloadPDSMembers(pdsName, toDir, ext = "txt", issuesErrorMessages = True):
    if not ext:
        ext = '""'
    result = run("zowe files download am " + pdsName + " -d " + toDir + " -e " + ext, issuesErrorMessages)
    if result.stdout:
        return True
    else:
        return False 

#downloadPDSMembers("")

def submitLocal(jclName,  issuesErrorMessages = True):
    result = run("zowe jobs sub lf  " + jclName + " --rfj", issuesErrorMessages)
    if result.stdout:
        jobDetails = json.loads(result.stdout)
        return jobDetails['data']['jobid'].upper()
    else:
        return ''

def jobStatus(jobid, issuesErrorMessages = True):
    result = run("zowe jobs view jsbj " + jobid + " --rfj", issuesErrorMessages)
    if result.stdout:
        jobDetails = json.loads(result.stdout)
        return jobDetails['data']
    else:
        return ''

def getPDSMembers(pdsName, issuesErrorMessages = True):
    result = run("zowe files list am  " + pdsName + " --rfj")
    if result.stdout:
        members = json.loads(result.stdout)
        return members['stdout']
    else:
       return ''   

def downloadPDSContent(pdsName, membName, toDir, ext = ".txt", issuesErrorMessages = True):
    if not ext:
        ext = '""'
    result = run("zowe files download ds \"" + pdsName + "(" + membName + ")\"" +  " -f " + toDir + membName + ext, issuesErrorMessages)
    if result.stdout:
        return True
    else:
        return False 
        
def submitRemote(pdsName, membName,  issuesErrorMessages = True):
    result = run("zowe jobs sub ds  \"" + pdsName + "(" + membName + ")\" --rfj", issuesErrorMessages)
    if result.stdout:
        jobDetails = json.loads(result.stdout)
        return jobDetails['data']['jobid'].upper()
    else:
        return ''

def jobWaitForComplete(jobid, highestValidReturnCode = 0, checkFrequemcy = 1, timeoutInterations = 60, issuesErrorMessages = True):
    complete = False
    numberInterations = 0

    statusInds = "\\|/-"

    while not complete:
        results = jobStatus(jobid, issuesErrorMessages)

        # if the job is complete
        if results['status'] == "OUTPUT":
            complete = True

            # Extract the return code and convert to number ('RC 0000', 'JCL ERROR')
            # If it fails then there was an error
            try:
                retcode = int((results['retcode'])[-4:])
            except ValueError:
                return False

            # Check the highest valid return code and if JCL Return Code is greater then not successful 
            if retcode > highestValidReturnCode:
                return False
        else:
            if issuesErrorMessages:
                index = numberInterations % 4
                print(statusInds[index], end="\r")

            numberInterations += 1
            if numberInterations > timeoutInterations:
                if issuesErrorMessages:
                    print("Timeout: JCL running longer than expected")
                return False

            # wait 'n' seconds to check again
            time.sleep(checkFrequemcy)

    return True
