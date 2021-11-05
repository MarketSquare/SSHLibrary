*** Settings ***
Force Tags      pybot   jybot
Resource        resources/sftp.robot
Suite Setup     Login And Upload Test Files
Suite Teardown  Remove Test Files and Close Connections

*** Test Cases ***
Directory Should Exist Using Absolute Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT}
    SSH.Directory Should Exist  ${target}
    Run Keyword And Expect Error  Directory '${target}' exists.
    ...                           SSH.Directory Should Not Exist  ${target}

Directory Should Not Exist Using Absolute Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT}/not_exists
    SSH.Directory Should Not Exist  ${target}
    Run Keyword And Expect Error  Directory '${target}' does not exist.
    ...                           SSH.Directory Should Exist  ${target}

Directory Should Exist Using Relative Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}/${SUBDIRECTORY NAME}
    SSH.Directory Should Exist  ${target}
    Run Keyword And Expect Error  Directory '${target}' exists.
    ...                           SSH.Directory Should Not Exist  ${target}

Directory Should Not Exist Using Relative Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}/not_exists
    SSH.Directory Should Not Exist  ${target}
    Run Keyword And Expect Error  Directory '${target}' does not exist.
    ...                           SSH.Directory Should Exist  ${target}

Directory Should Exist Using Current Path
    ${target} =  Set Variable  .
    SSH.Directory Should Exist  ${target}
    Run Keyword And Expect Error  Directory '${target}' exists.
    ...                           SSH.Directory Should Not Exist  ${target}

File Should Exist Using Absolute Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}
    SSH.File Should Exist  ${target}
    Run Keyword And Expect Error  File '${target}' exists.
    ...                           SSH.File Should Not Exist  ${target}

File Should Not Exist Using Absolute Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT}/not_exists
    SSH.File Should Not Exist  ${target}
    Run Keyword And Expect Error  File '${target}' does not exist.
    ...                           SSH.File Should Exist  ${target}

File Should Exist Using Relative Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}/${SUBDIRECTORY NAME}/${FILE WITH NON-ASCII NAME}
    SSH.File Should Exist  ${target}
    Run Keyword And Expect Error  File '${target}' exists.
    ...                           SSH.File Should Not Exist  ${target}

File Should Not Exist Using Relative Path
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}/not_exists
    SSH.File Should Not Exist  ${target}
    Run Keyword And Expect Error  File '${target}' does not exist.
    ...                           SSH.File Should Exist  ${target}

File Should Exist Using GLOB Patterns
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}/${SUBDIRECTORY NAME}/?[a][!b]*.txt
    SSH.File Should Exist  ${target}

File Should Not Exist Using GLOB Patterns
    ${target} =  Set Variable  ${REMOTE TEST ROOT NAME}/${SUBDIRECTORY NAME}/?[a]z[!b]*.txt
    SSH.File Should Not Exist  ${target}

Directory Should Exist Using GLOB Patterns
    ${target} =  Set Variable  ${REMOTE TEST ROOT}/[abcDAWF][!b]?*
    SSH.Directory Should Exist  ${target}

Directory Should Not Exist Using GLOB Patterns
    ${target} =  Set Variable  ${REMOTE TEST ROOT}/z*
    SSH.Directory Should Not Exist  ${target}
