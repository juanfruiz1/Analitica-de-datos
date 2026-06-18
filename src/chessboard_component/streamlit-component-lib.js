/**
 * Streamlit Component Library - Minimal vendored version.
 * Implements the Streamlit component protocol via window.parent.postMessage.
 * This replaces the npm streamlit-component-lib to avoid ESM/MIME-type issues
 * when served from Streamlit's static component directory.
 */
(function (window) {
    "use strict";

    var ComponentMessageType = {};
    ComponentMessageType.COMPONENT_READY = "streamlit:componentReady";
    ComponentMessageType.SET_COMPONENT_VALUE = "streamlit:setComponentValue";
    ComponentMessageType.SET_FRAME_HEIGHT = "streamlit:setFrameHeight";

    // Minimal EventTarget polyfill (browser-native EventTarget is used directly).
    var events;
    if (typeof EventTarget !== "undefined") {
        events = new EventTarget();
    } else {
        events = document.createElement("div");
    }

    function sendBackMsg(type, data) {
        window.parent.postMessage(Object.assign({ isStreamlitMessage: true, type: type }, data), "*");
    }

    var Streamlit = {
        API_VERSION: 1,
        RENDER_EVENT: "streamlit:render",
        events: events,
        registeredMessageListener: false,
        lastFrameHeight: null,

        setComponentReady: function () {
            if (!this.registeredMessageListener) {
                window.addEventListener("message", this.onMessageEvent.bind(this));
                this.registeredMessageListener = true;
            }
            sendBackMsg(ComponentMessageType.COMPONENT_READY, { apiVersion: this.API_VERSION });
        },

        setFrameHeight: function (height) {
            if (height === undefined) {
                height = document.body ? document.body.scrollHeight : 0;
            }
            if (height !== this.lastFrameHeight) {
                this.lastFrameHeight = height;
                sendBackMsg(ComponentMessageType.SET_FRAME_HEIGHT, { height: height });
            }
        },

        setComponentValue: function (value) {
            sendBackMsg(ComponentMessageType.SET_COMPONENT_VALUE, { value: value, dataType: "json" });
        },

        onMessageEvent: function (event) {
            if (event.data && event.data.type === this.RENDER_EVENT) {
                this.onRenderMessage(event.data);
            }
        },

        onRenderMessage: function (data) {
            var args = data.args || {};
            var disabled = Boolean(data.disabled);
            var theme = data.theme;
            var detail = { disabled: disabled, args: args, theme: theme };
            var renderEvent = new CustomEvent(this.RENDER_EVENT, { detail: detail });
            this.events.dispatchEvent(renderEvent);
        }
    };

    window.Streamlit = Streamlit;
})(window);
