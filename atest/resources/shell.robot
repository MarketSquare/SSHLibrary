*** Settings ***
Resource    common.robot


*** Variables ***
${LOCAL SCRIPTS}        ${LOCAL TESTDATA}${/}scripts
${TEST SCRIPT NAME}     test.sh
${TEST SCRIPT}          ${LOCAL SCRIPTS}${/}${TEST SCRIPT NAME}


*** Keywords ***
Login And Upload Test Scripts
    Login As Valid User
    Put Directory    ${LOCAL SCRIPTS}    ${REMOTE TEST ROOT}    recursive=True    newline=LF
