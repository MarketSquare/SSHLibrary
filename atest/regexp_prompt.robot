*** Settings ***
Default Tags   pybot   jybot
Resource       resources/common.robot
Test Teardown  Close All Connections

*** Test Cases ***
Read Until Prompt With Regexp Prompt
    Open Connection  localhost  prompt=[$|#]  prompt_is_regexp=yes
    Login  test  test
    Write  pwd
    ${output}=	Read Until Prompt
    Should Contain	${output}  $
    Write  su test_prompt
    ${password}=	Read	delay=0.5s
    Should Contain	${password}	Password:
    Write  test
    ${output1}=	Read Until Prompt
    Should Contain	${output1}  \#
    Write  exit
    ${output2}=	Read Until Prompt
    Should Contain	${output2}  $

Set Client Configuration With Regexp Prompt
    Open Connection  localhost  prompt=$
    Login  test  test
    Write  pwd
    ${output}=	Read Until Prompt
    Should Contain	${output}  $
    Set Client Configuration  prompt=[$|#]  prompt_is_regexp=yes
    Write  su test_prompt
    ${password}=	Read	delay=0.5s
    Should Contain	${password}	Password:
    Write  test
    ${output1}=	Read Until Prompt
    Should Contain	${output1}  \#
    Write  exit
    ${output2}=	Read Until Prompt
    Should Contain	${output2}  $
