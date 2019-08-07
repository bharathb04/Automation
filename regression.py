#! /usr/bin/python
import json
import sys
import os
# Some ZOWE commands Python'ised
import zowe

def main():

    """
    Regression suite

    """
    # Get the userid from the first Zowe z/OSMF profile (assumed default user)``
    zoweUser  = zowe.getDefaultZosmfUser()
    userID = zoweUser.user
    if not userID:
        print("unable to obtain user details.\nPrerequisite: Zowe - Open source mainframe CLI with a default z/OSMF profile defined.")
        sys.exit()
    print("Default user for session : " + userID)
    print("On host : " + zoweUser.host)

    # Get Datasets In a List
    membList = []
    workDir = "C:\\Users\\" + userID + "\\"
    dataSet = "DEv"
    members = zowe.getPDSMembers(dataSet)
    membList = members.split('\n')
    #print("List of datasets:" + str(membList[2]))
    
    # Perform Auto-Regression for JCL members
    for jcl in membList:
        if jcl:
           executeJCL(jcl, dataSet) 
           verifyRC(jcl, workDir)       
           
# executeJCL function will submit a JCL, wait for it's completion then returns control to main on successful job completion
def executeJCL(job, pdsName):
  
    jobId = zowe.submitRemote(pdsName, job)
    
    # Wait for the job to complete and issue error for any problems.
    if not zowe.jobWaitForComplete(jobId, 8):
        reason = zowe.jobStatus(jobId)
        print("job failed. Review job output") 
        print("Job Name    : " + str(reason['jobname']))
        print("Job ID      : " + jobId)
        print("Return Code : " + str(reason['retcode']))
        sys.exit()
    return ''


# verifyRC function will download the BTS output dataset, check the return code and interpret it. Then deletes the downloaded file on exit
def verifyRC(job, userDirectory):

    outFile = userDirectory + job + '.txt'    
    outdataSet = "DEV"
    testCaseSfx = job[5:] 
    
    if zowe.downloadPDSContent(outdataSet, job, userDirectory): 
        with open(outFile, encoding="utf8") as f:
            rc_record = f.readline().split('  ') 
        if rc_record[3] == 'S':                        
            print("Test case TC-VIEW-" + testCaseSfx + " Pass")
        elif rc_record[3] == 'E':
            print("Test case TC-VIEW-" + testCaseSfx + " Failed")
        else:
            print("Return Code Invalid, please check the BTS JCL for view " + testCaseSfx)

        os.remove(outFile) 

    return ''
# -----------------------------------------------------------------------------------


if __name__ == "__main__":
    main()
    sys.exit()


