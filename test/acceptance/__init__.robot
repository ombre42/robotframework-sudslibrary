*** Settings ***
Suite Setup       Start Services    ${SERVER TYPE}
Suite Teardown    Stop Services
Resource          resource.txt
