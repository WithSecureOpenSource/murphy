/*
Copyright (c) 2011-2013 F-Secure
See LICENSE for details
*/

function removeChilds(elem) {
    while (elem.hasChildNodes()) {
        elem.removeChild(elem.lastChild);
    }
}

function clear_select(select_elem) {
    while (select_elem.length > 0) {
        select_elem.remove(0);
    }
}

function load_select_with_array(select_elem, elements, add_empty_option) {
    var option, i;
    clear_select(select_elem);
    if (add_empty_option) {
        option = document.createElement("option");
        option.text = "";
        select_elem.add(option);
    }
    for (i = 0; i < elements.length; i += 1) {
        option = document.createElement("option");
        option.text = elements[i];
        select_elem.add(option);
    }
}

function setCookie(c_name,value,exdays)
{
    var exdate=new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var c_value=escape(value) + ((exdays==null) ? "" : "; expires="+exdate.toUTCString());
    document.cookie=c_name + "=" + c_value;
};

function getCookie(c_name)
{
    var i,x,y,ARRcookies=document.cookie.split(";");
    for (i=0;i<ARRcookies.length;i++) {
        x=ARRcookies[i].substr(0,ARRcookies[i].indexOf("="));
        y=ARRcookies[i].substr(ARRcookies[i].indexOf("=")+1);
        x=x.replace(/^\s+|\s+$/g,"");
        if (x==c_name) {
            return unescape(y);
        }
    }
};
