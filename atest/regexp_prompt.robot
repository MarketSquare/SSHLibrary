*** Settings ***
Default Tags   pybot   jybot
Resource       resources/common.robot
Test Teardown  Close All Connections

*** Test Cases ***
Read Until Prompt With Regexp Prompt
    Open Connection  localhost  prompt=REGEXP:[$#]
    Login  test  test
    Write  pwd
    ${output}=	Read Until Prompt
    Should Contain	${output}  $
    Write  export PS1\='\\u\@\\h \\W # '
    ${output1}=	Read Until Prompt
    Should Contain	${output1}  \#
    [Teardown]  Close connection

Set Client Configuration With Regexp Prompt
    Open Connection  localhost  prompt=$
    Login  test  test
    Write  pwd
    ${output}=	Read Until Prompt
    Should Contain	${output}  $
    Set Client Configuration  prompt=REGEXP:[$#]
    Write  export PS1\='\\u\@\\h \\W # '
    ${output1}=	Read Until Prompt
    Should Contain	${output1}  \#
    Write  export PS1\='\\u\@\\h \\W $ '
    ${output2}=	Read Until Prompt
    Should Contain	${output2}  $
