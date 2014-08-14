function addHandler(element, eventName, handler) {
    if (element.attachEvent) {
        return element.attachEvent('on' + eventName, handler);
    } else {
        return element.addEventListener(eventName, handler, false);
    }
}

function addHandlerToButtons(className, handler) {
    var buttons = getElementsByClassName(className);
    for (var i = buttons.length - 1; i >= 0; i--) {
        addHandler(buttons[i], 'click', handler);
    };

}

function getElementsByClassName(className) {
    if (document.getElementsByClassName) {
        return document.getElementsByClassName(className);
    } else {  // IE8
        return document.querySelectorAll('.' + className);
    }
}

function getIdAndVersion(evt) {
    var targetElement = (evt.srcElement) ? evt.srcElement : evt.currentTarget;
    var id = targetElement.value;
    return {
        'id' : id,
        'version' : document.getElementById(id).value
    };
}

function getViewUrl(targetId, targetVersion) {
    return targetVersion + '/' + targetId + '.html';
}

function viewDoc(event) {
    var target = getIdAndVersion(event);
    window.location.href = getViewUrl(target.id, target.version);
}

window.onload = function() {
    addHandlerToButtons('view-doc', viewDoc);
};
