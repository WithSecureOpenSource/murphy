<html>
<!--
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
-->
<head>
<script src="scripts/require.js"></script>
</head>
<body>
Creating project {{project_name}}...
<br>
<br>
</body>
<script>
require(["scripts/murphy/utils.js"], function (utils) {
    setTimeout(function () {
        document.body.appendChild(document.createTextNode("Preparing some stuff..."));
        document.body.appendChild(document.createElement("br"));
        document.body.appendChild(document.createElement("br"));
        setTimeout(function () {
            document.body.appendChild(document.createTextNode("Preparing some more stuff..."));
            document.body.appendChild(document.createElement("br"));
            document.body.appendChild(document.createElement("br"));
            setTimeout(function () {
                document.body.appendChild(document.createTextNode("We're almost there..."));
                document.body.appendChild(document.createElement("br"));
                document.body.appendChild(document.createElement("br"));
                setTimeout(function () {
                    window.location.href = window.location.origin + "/murphy/main.html";
                }, 2000);
            }, 2000);
        }, 2000);
    }, 2000);
    utils.setCookie("autoscrap", "{{project_name}}.json", 1);
});
</script>
</html>
