var firefox = false;
var locations, rotationDelay = 5, rotating, agents, cyclerotate, shufflerotate;
;
var agentsDefaults = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36 Edg/117.0.2045.55",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/117.0.5938.132 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/21.0 Chrome/117.0.5938.132 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36 OPR/103.0.4928.45",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36 Brave/117.1.56.120"
];

const deleteValues = [
    {
        id: "cache",
        description: "temporary files stored to speed up loading"
    },
    {
        id: "cookies",
        description: "data stored by websites to remember you"
    },
    {
        id: "history",
        description: "list of websites you have visited"
    },
    {
        id: "downloads",
        description: "history of downloaded files"
    },
    {
        id: "formData",
        description: "information entered into forms"
    },
    {
        id: "localStorage",
        description: "website-specific stored data"
    },
    {
        id: "passwords",
        description: "saved login credentials"
    },
    {
        id: "fileSystems",
        description: "data stored by the File System API"
    },
    {
        id: "indexedDB",
        description: "noSQL database for client-side storage"
    },
    {
        id: "serviceWorkers",
        description: "background scripts for handling requests"
    },
    {
        id: "webSQL",
        description: "database storage in browsers"
    }
];

function bpOnLoad() {

    document.getElementById("editProxyList").addEventListener("click", editProxyList);
    document.getElementById("addProxyOK").addEventListener("click", addProxyOK);
    document.getElementById("addProxyCancel").addEventListener("click", addProxyCancel);
    document.getElementById("selectProxy").addEventListener("change", selectProxyChange);
    document.getElementById("autoReload").addEventListener("click", autoReloadClick);

    document.getElementById("editUserAgentList").addEventListener("click", editUserAgentList);
    document.getElementById("addUserAgentCancel").addEventListener("click", addProxyCancel);
    document.getElementById("addUserAgentOK").addEventListener("click", editUserAgentOK);

    document.getElementById("selectUserAgent").addEventListener("change", selectUserAgent);


    document.getElementById("excludeOptions").addEventListener("click", excludeOptions);
    document.getElementById("excludeOK").addEventListener("click", excludeOK);

    document.getElementById("deleteOptions").addEventListener("click", deleteOptions);
    document.getElementById("optionsOK").addEventListener("click", optionsOK);

    document.getElementById("blockOptions").addEventListener("click", blockOptions);

    document.getElementById("blockOK").addEventListener("click", blockOK);

    document.getElementById("rotateOK").addEventListener("click", rotateOK);
    document.getElementById("rotateCancel").addEventListener("click", rotateCancel);
    document.getElementById("stopRotation").addEventListener("click", stopRotation);

    document.getElementById("about").addEventListener("click", about);
    document.getElementById("aboutOK").addEventListener("click", aboutOk);

    document.getElementById("testMyProxies").addEventListener("click", testMyProxies);

    document.getElementById("proxiesType").addEventListener("change", proxiesTypeChanged);
    document.getElementById("forcePrivacy").addEventListener("click", forcePrivacy);
    document.getElementById("bandwidthOptions").addEventListener("click", bandwidthOptions);
    document.getElementById("bandwidthOK").addEventListener("click", bandwidthOK);

    updateProxySelect();


}
function bandwidthOptions() {
    loadOpt("excludeList", async (res) => {
        document.getElementById('changeProxyNotification').checked = res.changeProxyNotification;
        document.getElementById('deleteCookiesNotification').checked = res.deleteCookiesNotification;
    });

    switchTab(8);
}

function bandwidthOK() {
    saveOpt("changeProxyNotification", document.getElementById('changeProxyNotification').checked);
    saveOpt("deleteCookiesNotification", document.getElementById('deleteCookiesNotification').checked);
    switchTab(1);
}

function forcePrivacy() {
    chrome.runtime.sendMessage({action: 'deleteOptions'});
}

function proxiesTypeChanged() {
    if (document.getElementById("proxiesType").selectedIndex > 0) {
        document.getElementById("socksWarning").style.display = "block";
    } else {
        document.getElementById("socksWarning").style.display = "none";
    }

}
function testMyProxies() {
    //  $("#typeOfProxies").val(bg.loadConf("proxiesType"));
    $("#testmyproxiesForm").submit();
}

function editUserAgentOK() {
    switchTab(1);
    agents = sanitizeProxies(document.getElementById("userAgentsTextArea").value, 1);
    saveOpt("userAgents", agents);
    updateProxySelect();
}

function editUserAgentList() {
    document.getElementById("userAgentsTextArea").value = agents.join("\n");
    switchTab(6);
}

function about() {
    document.getElementById("monkey").src = getImageURL("img/monkey.gif");

    switchTab(4);
}

function aboutOk() {
    switchTab(1);
}

function stopRotation() {
    chrome.runtime.sendMessage({action: 'stopRotation', text: ""});
}

function stopRotationBg() {
    rotating = false;
    document.getElementById("rotatingText").innerHTML = "<b>Rotation complete</b>";
    $('#rotatingText').delay(10000).fadeOut('slow');

    document.getElementById("stopRotation").style.display = "none";


}

function rotateCancel() {
    showHide('proxySelectDiv', 'proxyRotationDiv');
    switchTab(1);
}

function rotateOK() {
    rotationDelayNew = document.getElementById('rotateSeconds').value;

    loadOpt("excludeList", async (res) => {


        if (rotationDelayNew < 1) {
            alert("Please enter a bigger delay");
        } else if (res.proxiesList.toString().split(",").length < 3) {
            alert("You need to have at least 3 proxies on your list");
        } else {

            saveOpt("rotationDelay", rotationDelayNew);
            saveOpt("cyclerotate", document.getElementById('cyclerotate').checked);
            saveOpt("shufflerotate", document.getElementById('shufflerotate').checked);

            rotationDelay = rotationDelayNew;

            switchTab(1);
            chrome.runtime.sendMessage({action: 'startRotation', text: rotationDelay});
            document.getElementById("stopRotation").style.display = "block";

            $("#testMyproxies").hide();
        }
    });
}


function showHide(id1, id2) {
    document.getElementById(id1).style.display = "block";
    document.getElementById(id2).style.display = "block";

    if (id2 == "proxyRotationDiv") {
        $("#testMyProxies").show();
    }

    if (id1 == "proxyRotationDiv") {
        $("#testMyProxies").hide();
    }
}
function optionsOK() {

    deleteValues.forEach(del => {
        saveOpt(del.id, document.getElementById(del.id).checked);
    }
    );

    saveOpt("timeIntervalIndex", document.getElementById("timeInterval").selectedIndex);
    saveOpt("timeInterval", document.getElementById("timeInterval").value);

    switchTab(1);

}

function excludeOptions() {
    switchTab(10);
    loadOpt("excludeList", async (res) => {
        if (res.excludeList) {
            document.getElementById("excludeListTextarea").value = res.excludeList;
        }
    });
}

function excludeOK() {
    const exclude = Array.from(sanitizeProxies(document.getElementById("excludeListTextarea").value));
    saveOpt("excludeList", exclude.join("\n"));

    chrome.runtime.sendMessage({action: 'putProxy', text: ""});

    switchTab(1);
}


function switchTab(tab) {

    for (i = 1; i < 11; i++) {
        if (i === tab) {
            document.getElementById("tab" + i).style.display = "block";
        } else {
            document.getElementById("tab" + i).style.display = "none";
        }
    }

    if (tab == 2) {
        try {
            if (typeof $("#proxiesTextArea").parent().attr("class") == "undefined") {
                $("#proxiesTextArea").linedtextarea();
            }
        } catch (e) {
        }
    } else if (tab == 6) {
        try {
            if (typeof $("#userAgentsTextArea").parent().attr("class") == "undefined") {
                $("#userAgentsTextArea").linedtextarea();
            }
        } catch (e) {
        }
    }

}

function deleteOptions() {
    switchTab(3);

    // Load options using loadOpt and process them
    loadOpt("opt", async (res) => {
        // if (res.blockURLs) {
        clearForm("privacy"); // Clear the existing form elements in 'privacy'

        // Iterate over deleteValues array to create checkboxes dynamically
        deleteValues.forEach(del => {
            // Create a div for each checkbox and description
            var div = document.createElement("div");
            div.style.marginBottom = "3px"; // Add space between rows

            // Create checkbox input element
            var option = document.createElement("input");
            option.type = "checkbox";
            option.id = del.id; // Set the ID of the checkbox

            // Check if the current delete value is set in the response and set the checkbox accordingly
            if (res[del.id]) {
                option.checked = true;
            }

            // Append checkbox to the div
            div.appendChild(option);

            // Create a label with bold text for ID and description
            var label = document.createElement("label");
            label.htmlFor = del.id; // Associate label with checkbox

            // Create bold text for del.id
            var boldText = document.createElement("underline");
            boldText.textContent = `${del.id} `;
            label.appendChild(boldText);

            label.appendChild(document.createTextNode("(" + del.description + ")"));

            // Append label to the div
            div.appendChild(label);

            // Append the div to the 'privacy' container
            document.getElementById("privacy").appendChild(div);
        });

        // Set the selected index for the timeInterval element
        document.getElementById("timeInterval").selectedIndex = res["timeIntervalIndex"];

        // }
    });
}

function blockOptions() {
    loadOpt("opt", async (res) => {

        document.getElementById("blockURLs").value = makeVal(res.blockURLs, "");
        document.getElementById("webRTC").checked = res.webRTC;

    });
    switchTab(7);
}


function blockOK() {
    changeWebRtc(document.getElementById("webRTC").checked);

    saveOpt("webRTC", document.getElementById("webRTC").checked);
    saveOpt("blockURLs", document.getElementById("blockURLs").value);


    blocked = sanitizeProxies(document.getElementById("blockURLs").value);

    chrome.runtime.sendMessage({action: 'updateBlocked', urls: blocked});

    switchTab(1);
}


function changeWebRtc(block) {

    chrome.privacy.network.webRTCIPHandlingPolicy.set({
        value: block ? 'disable_non_proxied_udp' : 'default',
        scope: 'regular'
    });
}

function updateRules(userAgent) {

    if (userAgent === "NO CHANGE") {
        chrome.declarativeNetRequest.updateDynamicRules({
            removeRuleIds: [1]
        });

    } else {
        const rule = {
            "id": 1,
            "priority": 1,
            "action": {
                "type": "modifyHeaders",
                "requestHeaders": [
                    {
                        "header": "User-Agent",
                        "operation": "set",
                        "value": userAgent
                    }
                ]
            },
            "condition": {
                "urlFilter": "*",
                "resourceTypes": ["main_frame", "sub_frame"]
            }
        };

        chrome.declarativeNetRequest.updateDynamicRules({
            removeRuleIds: [1],
            addRules: [rule]
        });
    }
}

function editProxyList() {
    switchTab(2);
    loadOpt("proxiesList", async (res) => {
        if (res.proxiesList) {
            document.getElementById("proxiesTextArea").value = res.proxiesList.join("\n");
        }
        document.getElementById("getLocations").checked = res.getLocations;


    });


}


function addProxyOK() {
    switchTab(1);
    const proxies = sanitizeProxies(document.getElementById("proxiesTextArea").value);
    const getLocations = document.getElementById("getLocations").checked;
    saveOpt("proxiesList", proxies);
    saveOpt("proxiesType", document.getElementById("proxiesType").selectedIndex);
    saveOpt("getLocations", getLocations); //

    if (proxies.length > 0 && getLocations) {
        fetchProxyLocations(proxies, function () {
            updateProxySelect(true);
        });
    } else {
        updateProxySelect(true);
    }

}

function addProxyCancel() {
    switchTab(1);
}

function loadConf() {
    return 5;
}


function sanitizeProxies(prox) {

    try {
        prox = prox.toString().replace(/ /g, "");
        proxiesArr = prox.split("\n");
        proxiesNew = [];
        for (i = 0; i < proxiesArr.length; i++) {
            if (proxiesArr[i].length > 5) {

                proxiesNew.push(proxiesArr[i]);
            }
        }
        return proxiesNew.join("\n");
    } catch (e) {
        return prox;
    }
}


function saveOpt(opt, val) {
    let storageObject = {};
    storageObject[opt] = val;

    chrome.storage.local.set(storageObject, function () {

        console.log('saveOpt=' + opt + " val=" + val);
        chrome.runtime.sendMessage({action: 'updateBadgeText', text: ""});

    });
}

function loadOpt(val, callback) {
    chrome.storage.local.get(null, function (result) {

        callback(result || []);
    });
}

function makeVal(v, m) {
    if (typeof v === 'undefined') {
        {
            return m;

        }
    } else {
        return v;
    }
}

async function updateProxySelect(refresh = false) {

    clearForm('selectProxy');

    loadOpt("proxiesList", async (res) => {

        proxies = makeVal(res['proxiesList'], []);
        locations = makeVal(res['locations'], []);
        agents = makeVal(res['userAgents'], []);
        rotating = makeVal(res['rotating'], false);

        rotationDelay = makeVal(res['rotationDelay'], 5);
        shufflerotate = makeVal(res['rotationDelay'], false);
        cyclerotate = makeVal(res['cyclerotate'], false);

        console.log("cyclerotate " + cyclerotate);

        if (!agents || agents.length < 1) {
            agentsOpt = agentsDefaults.slice();

        } else {
            agentsOpt = agents.slice();

        }

        //agentsOpt.unshift("RANDOM ON EACH PROXY CHANGE");

        agentsOpt.unshift("NO CHANGE");

        populateSelect("selectUserAgent", agentsOpt);
        document.getElementById('selectUserAgent').selectedIndex = res['agentIndex'];


        document.getElementById('proxiesType').selectedIndex = res['proxiesType'];
        proxiesTypeChanged();

        document.getElementById('autoReload').checked = res['autoReload'];

        var select = document.getElementById('selectProxy');
        var fragment = document.createDocumentFragment();

        appendOption(fragment, 'NO PROXY', 'NOPROXY', 'noproxy.png', proxies.length > 0 ? 'No proxy' : 'No proxy. Add proxies from "edit" --------->>>');
        appendOption(fragment, `AUTOROTATE EVERY ` + rotationDelay + ` SECONDS`, 'AUTOROTATE', 'rotate.png', `Autorotate every ` + rotationDelay + ` seconds`);

        var selectedProxyIndex = res['selectedProxyIndex'];


        var n = 2;
        proxies.forEach(proxy => {
            if (proxy.length > 0) {

                if ((selectedProxyIndex != 1 || !rotating) && proxy == res['selectedProxy']) {
                    selectedProxyIndex = n;
                }
                const option = createProxyOption(proxy);
                fragment.appendChild(option);
                n++;
            }
        });


        if (res['selectedProxy'] === "NOPROXY") {
            selectedProxyIndex = 0;
        }


        select.appendChild(fragment);

        select.selectedIndex = selectedProxyIndex;
        $('.selectpicker').selectpicker('refresh');

        if (refresh) {
            $('.selectpicker').selectpicker('toggle');
        }

        if (rotating) {
            showHide('proxyRotationDiv', 'proxySelectDiv');
        } else {
            showHide('proxySelectDiv', 'proxyRotationDiv');
        }

        $("#proxiesHidden").val(proxies.join(";"));

    });

}

function populateSelect(selectId, options) {
    const selectElement = document.getElementById(selectId);

    // Clear any existing options
    selectElement.innerHTML = "";

    // Create and append the options
    options.forEach(option => {
        const optionElement = document.createElement("option");
        optionElement.value = option;
        optionElement.textContent = option;
        selectElement.appendChild(optionElement);
    });
}

function createProxyOption(proxy) {
    const option = document.createElement('option');
    const parsedProxy = parseProxy(proxy);
    const location = locations[parsedProxy[0]];
    const locationTxt = location ? `<img style='width:40px;height:20px;margin-right:5px;' src='${getImageURL(`img/flags/${location.toLowerCase()}.png`)}'>` : '';
    option.value = proxy;
    const label = parsedProxy.length === 5 ? `${parsedProxy[4]} (${parsedProxy[0]})` : parsedProxy.length === 3 ? `${parsedProxy[2]} (${parsedProxy[0]})` : parsedProxy[0];
    option.setAttribute('data-content', locationTxt + label);
    return option;
}

function getImageURL(img) {
    if (firefox) {
        return   browser.runtime.getURL(img)
    } else {
        return chrome.runtime.getURL(img);
    }
}

function clearForm(id) {
    select = document.getElementById(id);
    while (select.firstChild) {
        select.removeChild(select.firstChild);
    }
}

function validateIPv4(ip) {
    ip = ip.split(":");
    ip = ip[0];
    const ipv4Regex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipv4Regex.test(ip);
}

function parseProxy(proxy) {
    var p = proxy.split(':'), out = [];
    if (p.length > 7) {
        var ip = [];
        for (i = 0; i < 8; i++) {
            ip.push(p[i].trim());
        }
        out[0] = ip.join(":");
        out[1] = p[8].trim();
        out[2] = p[9].trim();
        out[3] = p[10].trim();
        if (p.length > 11) {
            out[4] = p[11].trim();
        }

    } else {
        for (i = 0; i < p.length; i++) {
            out[i] = p[i].trim();
        }
    }
    return out;
}
function showSpinner() {
    document.getElementById('spinner').style.display = 'block';
}

function hideSpinner() {
    document.getElementById('spinner').style.display = 'none';
}

function sanitizeProxies(prox, limit = 4) {

    try {
        if (limit != 1) {
            prox = prox.toString().replace(/ /g, "");
        }
        proxiesArr = prox.split("\n");
        proxiesNew = [];
        for (i = 0; i < proxiesArr.length; i++) {
            if (proxiesArr[i].length > limit) {
                proxiesNew.push(proxiesArr[i]);
            }
        }
        return proxiesNew;
    } catch (e) {
        return prox;
}
}




function selectUserAgent() {
    saveOpt("agent", document.getElementById("selectUserAgent").value);
    saveOpt("agentIndex", document.getElementById("selectUserAgent").selectedIndex);
    updateRules(document.getElementById("selectUserAgent").value);
}



function setProxy(proxy) {
    saveOpt("selectedProxy", proxy);
    chrome.runtime.sendMessage({action: 'putProxy', text: proxy});
}







function autoReloadClick() {
    saveOpt("autoReload", document.getElementById("autoReload").checked);
}

function selectProxyChange() {

    const selectProxy = document.getElementById("selectProxy");
    saveOpt("selectedProxyIndex", selectProxy.selectedIndex);

    if (select.value == "NOPROXY") {
//        bg.cancelProxy();
        setProxy(selectProxy.value);

    } else if (select.value == "AUTOROTATE") {
        document.getElementById("rotateSeconds").value = rotationDelay;
        document.getElementById('cyclerotate').checked = cyclerotate;
        document.getElementById('shufflerotate').checked = shufflerotate;
        switchTab(5);
    } else {

        setProxy(selectProxy.value);

    }


}

async function fetchProxyLocations(proxies, callback) {

    proxies = proxies.filter(validateIPv4);
    const ips = proxies.map(proxy => parseProxy(proxy)[0]).join('-'); // Extract IPs and join them with '-'
    const url = `https://testmyproxies.com/_scripts/showLocations.php?ips=${ips}`;
    var locations = {};
    try {
        const response = await fetch(url);
        locations = await response.json();
        saveOpt("locations", locations);
        return callback(); // Adjust based on the actual API response structure
    } catch (error) {

        console.log('Error fetching proxy locations:' + error);

        saveOpt("locations", locations);
        callback();
    }
}

function appendOption(fragment, text, value, imgSrc, contentText) {
    const option = document.createElement('option');
    option.text = text;
    option.value = value;
    const locationTxt = `<img style='width:40px;height:20px;margin-right:5px;' src='${getImageURL(`img/flags/${imgSrc}`)}'>`;
    option.setAttribute('data-content', locationTxt + contentText);
    fragment.appendChild(option);
}


chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action === "startRotationBg") {
        rotating = true;
    } else if (request.action === "stopRotationBg") {
        stopRotationBg();
        rotating = false;
    } else if (rotating && request.action === "rotatingSeconds") {
        updateRotatingText(request.data);

    }
    updateProxySelect();

});

function updateRotatingText(sec) {


    document.getElementById("rotatingText").innerHTML = "Rotating to the next proxy in <b>" + sec + " seconds</b>";
    document.getElementById("stopRotation").style.display = "block";




}

document.addEventListener('DOMContentLoaded', bpOnLoad, false);

