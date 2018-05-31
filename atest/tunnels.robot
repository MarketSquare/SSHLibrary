*** Settings ***
Force Tags     pybot   jybot
Resource       resources/common.robot
Test Setup     Open Connection  ${HOST}
Test Teardown  Close All Connections
Library        OperatingSystem

*** Variables ***
${KEY DIR}           ${LOCAL TESTDATA}${/}keyfiles
${KEY USERNAME}      testkey
${KEY}               ${KEY DIR}${/}id_rsa

*** Test Cases ***
Local Tunnel
    Login  test  test
    Create Local SSH Tunnel  9192  google.com  80
    ${result}  Run Netstat
    Should Contain  ${result}  :9192

Local Tunnel With Public Key
    Login With Public Key  ${KEY USERNAME}  ${KEY}
    Create Local SSH Tunnel  9193  google.com  80
    ${result}  Run Netstat
    Should Contain  ${result}  :9193

*** Keywords ***
Run Netstat
    ${result}  Run Keyword If  os.sep == '/'
    ...  Run  netstat -tulpn
    ...  ELSE
    ...  Run  netstat -an
    [Return]  ${result}
    
