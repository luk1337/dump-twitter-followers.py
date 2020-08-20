#1/bin/bash
curl -s $(curl https://twitter.com -s | grep -Eom1 'https://abs.twimg.com/responsive-web/client-web-legacy/main.[0-9a-z]+.js') | grep -Eo 'e.exports={queryId:"[0-9a-zA-Z]+",operationName:"[0-9a-zA-Z]+",operationType:"[0-9a-zA-Z]+"}'
