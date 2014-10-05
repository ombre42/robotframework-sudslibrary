*** Settings ***
Resource        resource.txt

*** Test Cases ***
Http Authentication
    Create Soap Client    ${TEST WSDL URL}
    Set Location    ${SECURE TEST URL}
    Run Keyword And Expect Error    (401, u'Authentication Required')    Call Soap Method    theAnswer
    Set Http Authentication    bob    bob    STANDARD
    ${answer}    Call Soap Method    theAnswer
    Should Be Equal    ${answer}    ${42}
    Create Soap Client    ${TEST WSDL URL}
    Set Http Authentication    bob    foo    ALWAYS_send
    ${sum}    Call Soap Method    theAnswer
    ${request}    Get Sent Request
    # auth not needed, but should have been sent anyways
    Should Be Equal As Strings    ${request.headers['Authorization']}    Basic Ym9iOmZvbw==
    Run Keyword And Expect Error    ValueError: 'bad' is not a supported type.    Set Http Authentication    bob    foo    bad