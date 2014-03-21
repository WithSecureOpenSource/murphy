/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

/*jslint indent: 4, maxerr: 50, passfail: false, nomen: true*/
/*global define, document*/

define(function () {
    "use strict";
    var NewModelView = function (container_element, on_cancel) {
        var _container = container_element;

        this.show = function () {
            var frame = document.createElement("form"),
                elem,
                a_button;

            frame.action = "request_create.html";
            frame.method = "post";
            frame.enctype = "multipart/form-data";

            frame.style.margin = "10px";
            frame.appendChild(document.createElement("br"));
            elem = document.createTextNode("Creating a new project");
            frame.appendChild(elem);
            frame.appendChild(document.createElement("br"));
            frame.appendChild(document.createElement("br"));

            elem = document.createElement("input");
            elem.type = "file";
            elem.id = "file content";
            elem.name = "file content";
            frame.appendChild(elem);
            frame.appendChild(document.createElement("br"));
            frame.appendChild(document.createElement("br"));
            elem.addEventListener("change", function () {
                var filename = this.value.split("/").pop().split("\\").pop(),
                    parts = filename.split(".");
                parts.pop();
                parts = parts.join(".");
                if (parts !== "") {
                    filename = parts;
                }
                document.getElementById("new project name").value = filename;
            });

            elem = document.createElement("label");
            elem.htmlFor = "new project name";
            elem.appendChild(document.createTextNode("Name of the project"));
            frame.appendChild(elem);
            frame.appendChild(document.createElement("br"));

            elem = document.createElement("input");
            elem.type = "text";
            elem.id = "new project name";
            elem.name = "new project name";
            frame.appendChild(elem);
            frame.appendChild(document.createElement("br"));
            frame.appendChild(document.createElement("br"));

            elem = document.createElement("label");
            elem.htmlFor = "overwrite";
            elem.appendChild(document.createTextNode("Overwrite if exists"));
            frame.appendChild(elem);

            elem = document.createElement("input");
            elem.type = "checkbox";
            elem.id = "overwrite";
            elem.name = "overwrite";
            elem.checked = true;
            frame.appendChild(elem);

            elem = document.createElement("label");
            elem.htmlFor = "start scraping";
            elem.appendChild(document.createTextNode("Start scraping after creation"));
            frame.appendChild(elem);

            elem = document.createElement("input");
            elem.type = "checkbox";
            elem.id = "autostart";
            elem.name = "autostart";
            elem.checked = true;
            frame.appendChild(elem);

            frame.appendChild(document.createElement("br"));
            frame.appendChild(document.createElement("br"));

            a_button = document.createElement("input");
            a_button.type = 'submit';
            a_button.value = 'Create';
            a_button.style.marginLeft = '10px';
            frame.appendChild(a_button);


            a_button = document.createElement("input");
            a_button.type = 'button';
            a_button.value = 'Cancel';
            a_button.style.marginLeft = '100px';
            a_button.addEventListener('click', on_cancel, false);
            frame.appendChild(a_button);

            _container.appendChild(frame);
        };
    };
    return {NewModelView: NewModelView};
});

