var locations, selectedProxyIndex, proxies, agents, selectedProxy, autoReload, excludeList, rotateProxyTimer, rotateCurrent, proxiesList, rotationDelay = 5, shufflerotate, cyclerotate;
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

function makeVal(v, m) {
    if (typeof v === 'undefined') {
        {
            return m;

        }
    } else {
        return v;
    }
}

function updateBadgeText() {


    loadOpt("proxiesList", async (res) => {

        console.log("updateBadgeText");
        proxiesList = makeVal(res['proxiesList'], []);
        locations = makeVal(res['locations'], []);
        agents = makeVal(res['userAgents'], []);
        autoReload = res['autoReload'];
        proxy = makeVal(res['selectedProxy'], "NOPROXY");
        selectedProxyIndex = makeVal(res['selectedProxyIndex'], "NOPROXY");
        proxiesType = makeVal(res['proxiesType'], 0);
        excludeList = makeVal(res['excludeList'], false);
        cyclerotate = makeVal(res['cyclerotate'], false);
        shufflerotate = makeVal(res['shufflerotate'], false);

        locationTxt = "++";

        if (proxy === "NOPROXY") {
            locationTxt = "--";
        } else {
            const p = proxy.split(":");
            if (locations.hasOwnProperty(p[0])) {
                locationTxt = locations[p[0]];
            } else {
                locationTxt = "";
            }
        }


        chrome.action.setBadgeText({text: locationTxt});

        if (autoReload) {
            refreshTab();
        }
    });

}

function updateBlockedUrls(urls) {



    var rules = urls.map((url, index) => ({

            id: index + 1, // Unique ID for each rule
            priority: 1,
            action: {type: "block"},
            condition: {
                urlFilter: `*://*.${url}/*`, // Blocking all subdomains and paths
                resourceTypes: ["main_frame"],
            },
        }
        ));

    const rl = rules.length + 1;

    rules.push({
        "id": rl,
        "priority": 1,
        "action": {
            "type": "modifyHeaders",
            "responseHeaders": [
                {
                    "header": "Set-Cookie",
                    "operation": "set",
                    "value": "Secure; HttpOnly"
                }
            ]
        },
        "condition": {
            "urlFilter": "*://*/*",
            "resourceTypes": ["main_frame"]
        }
    });


    // Clear existing rules and add new ones
    chrome.declarativeNetRequest.getDynamicRules(existingRules => {
        const existingRuleIds = existingRules.map(rule => rule.id);
        chrome.declarativeNetRequest.updateDynamicRules({
            removeRuleIds: existingRuleIds,
            addRules: rules,
        });
    });


}

function putProxy() {


    loadOpt("proxiesList", async (res) => {

        deleteOptions();

        proxy = res.selectedProxy;

        const p = proxy.split(":");

        console.log("putProxy3 " + p);

        const proxiesType = res.proxiesType;

        if (p[1] === '4444') {
            scheme = "http";
            p[1] = 80;
        } else if (proxiesType === 1) {
            scheme = "socks5";
        } else {
            scheme = "http";
        }

        var pl = [];
        if (res.excludeList) {
            pl = res.excludeList.split("\n");
        }


        proxiesList = [];
        proxiesList.push("localhost");
        proxiesList.push("*testmyproxies.com")
        for (i = 0; i < pl.length; i++) {
            proxiesList.push("*" + pl[i]);
        }

        proxiesList = proxiesList.join(",");

        console.log(proxiesList);

        const proxyConfig = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: scheme,
                    host: p[0],
                    port: parseInt(p[1])
                },
                bypassList: [proxiesList]

            }
        };

        chrome.proxy.settings.set({
            value: proxyConfig,
            scope: 'regular'
        },
                () => {
            updateBadgeText();
            createNotification("Proxy set", p[0], "changeProxyNotification");


        }
        );
    }
    );
}





function clearProxy() {
    saveOpt("selectedProxy", "NOPROXY");
    chrome.proxy.settings.clear(
            {
                scope: 'regular'
            },
            () => {
        createNotification("Proxy disabled", "NO proxy", "changeProxyNotification");

    }
    );
}

function onInstall() {


// Create a context menu
    chrome.contextMenus.create({
        id: "BpMenu1",
        title: "Delete cookies and cache",
        contexts: ["page"]
    });


    chrome.contextMenus.onClicked.addListener((info, tab) => {
        console.log("Bp Menu 1");
        if (info.menuItemId === "BpMenu1") {
            // Action when context menu is clicked
            if (!tab.url.startsWith("chrome://")) {
                console.log("Bp Menu 2");
                deleteOptions();
            }
        }
    });

    saveOpt("getLocations", "true");
    saveOpt("autoReload", "true");
    saveOpt("changeProxyNotification", "true");

    chrome.tabs.create({
        url: "about:blank"
    });


}


function saveOpt(opt, val) {
    let storageObject = {};
    storageObject[opt] = val;

    chrome.storage.local.set(storageObject, function () {
        console.log('saveOptBG=' + opt + " val=" + val);
    });
}

function loadOpt(val, callback) {
    chrome.storage.local.get(null, function (result) {

        callback(result || []);
    });
}



chrome.runtime.onStartup.addListener(updateBadgeText);
chrome.runtime.onInstalled.addListener(onInstall);

function updateProxyConfig(proxyConfig) {
    let config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: proxyConfig.type,
                host: proxyConfig.host,
                port: parseInt(proxyConfig.port, 10)
            },
            bypassList: ["localhost", "testmyproxies.com"]
        }
    };
    chrome.proxy.settings.set({value: config, scope: 'regular'});
}


function refreshTab() {
    try {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            if (tabs && tabs[0] && tabs[0].id) {

                chrome.tabs.reload(tabs[0].id);
            }
        });
    } catch (e) {
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

    if (message.action === 'updateBadgeText' && message.text) {
        updateBadgeText();
    } else if (message.action === 'putProxy') {
        if (message.text === "NOPROXY") {
            clearProxy();
        } else {
            putProxy();
        }
        updateBadgeText();

    } else if (message.action === 'updateBlocked') {
        const urls = message.urls || [];
        updateBlockedUrls(urls);

    } else if (message.action === 'deleteOptions') {
        deleteOptions();

    } else if (message.action === 'startRotation') {

        saveOpt("rotating", true);
        loadOpt("proxiesList", async (res) => {

            console.log("updateBadgeText");
            proxiesList = res['proxiesList'];
            if (res.shufflerotate) {
                proxiesList = shuffle(proxiesList);
                saveOpt("proxiesList", proxiesList);

            }
            console.log("startRotation 001");

            rotationDelay = message.text;
            console.log("startRotation 002");
            startRotation();

        });


    } else if (message.action === 'stopRotation') {
        console.log("stopLocation!");
        stopRotation();
    }


});


function startRotation() {
    saveOpt("rotating", true);
    sendMsg("startRotationBg");
    rotateCurrent = 1;
    selectedProxyIndex = 2;
    console.log("startRotation 003");
    try {
        console.log("startRotation p=" + proxiesList);
    } catch (e) {
        console.log("errr e=" + e);
    }
    console.log("startRotation 004");

    proxy = proxiesList[0];
    saveOpt("selectedProxyIndex", selectedProxyIndex);
    saveOpt("selectedProxy", proxy);

    console.log("startRotation");

    putProxy();
    rotateProxyTimer = setInterval(rotateProxy, 1000);
}

function stopRotation() {
    clearInterval(rotateProxyTimer);
    saveOpt("rotating", false);
    sendMsg("stopRotationBg");

}

function sendMsg(action, data = "") {
    chrome.runtime.sendMessage({'action': action, 'data': data}, function (response) {
        if (chrome.runtime.lastError) {

        } else {

        }
    });
}
function getProxyRotationRemaining() {
    return rotationDelay - rotateCurrent;

}

function rotateProxy() {
    var seconds = getProxyRotationRemaining();
    if (seconds <= 0) {
        rotateToNextProxy();
        rotateCurrent = 0;
    } else {
        rotateCurrent++;
    }


    sendMsg("rotatingSeconds", seconds);


}

function shuffle(array) {
    let counter = array.length;
    while (counter > 0) {
        let index = Math.floor(Math.random() * counter);
        counter--;
        let temp = array[counter];
        array[counter] = array[index];
        array[index] = temp;
    }

    return array;
}

function rotateToNextProxy() {

    console.log(`proxiesList: ` + proxiesList.length);

    // proxiesList = getProxiesList();
    if (selectedProxyIndex < proxiesList.length + 1) {
        selectedProxyIndex = selectedProxyIndex + 1;

        console.log(" rotate to index=" + selectedProxyIndex + " proxy=" + proxiesList[selectedProxyIndex - 2]);

        proxy = proxiesList[selectedProxyIndex - 2];
        saveOpt("selectedProxy", proxy);
        saveOpt("selectedProxyIndex", selectedProxyIndex);
        putProxy();

    } else {

        if (cyclerotate) {

            if (shufflerotate) {
                createNotification("Rotation", "End of the proxy rotation. Shuffling the list AND starting again from the top", "changeProxyNotification");
                proxiesList = shuffle(proxiesList);
                saveOpt("proxiesList", proxiesList);
            } else {
                createNotification("Rotation", "End of the proxy rotation. Starting again from the top", "changeProxyNotification");
            }

            proxy = proxiesList[0];
            saveOpt("selectedProxy", proxy);
            saveOpt("selectedProxyIndex", 2);
            putProxy();

        } else {
            console.log(" end rotation ");

            clearInterval(rotateProxyTimer);
            stopRotation();
            createNotification("Rotation", "End of the proxy list was reached. Stoping the rotation", "changeProxyNotification");
        }
    }

}

function createNotification(title, message, v = "") {
console.log("v="+v);
    loadOpt("proxiesList", async (res) => {
        if (res[v]) {
            
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon128.png',
                title: title,
                message: message,
                priority: 2
            });
        }
    });
            
}



function deleteRecentCookies() {
    loadOpt("opt", async (res) => {
        if (res.cookies) {
            const oneHourAgo = Date.now() - 3600 * 1000 * res.timeInterval;

            chrome.cookies.getAll({}, (cookies) => {
                if (!cookies) {
                    console.error("Failed to retrieve cookies.");
                    return;
                }

                cookies.forEach((cookie) => {
                    // Check if the cookie was created or modified in the last hour
                    if (!cookie.expirationDate || (cookie.expirationDate * 1000 > oneHourAgo)) {
                        const url = `http${cookie.secure ? 's' : ''}://${cookie.domain}${cookie.path}`;

                        // Remove the cookie
                        chrome.cookies.remove({url, name: cookie.name}, (result) => {
                            if (result) {
                                console.log(`Removed cookie: ${cookie.name} from ${url}`);
                            } else {
                                console.error(`Failed to remove cookie: ${cookie.name} from ${url}`);
                            }
                        });
                    }
                });
            });

            createNotification("Cookies were deleted", "Cookies were deleted", "deleteCookiesNotification");
        }
    });


}
function deleteOptions() {

    console.log("deleteOptions");

    var k = [];
    var dataTypesToClear = {};
    var n = 0;
    loadOpt("opt", async (res) => {
        deleteValues.forEach(del => {
            try {

                if (res[del.id]) {
                    dataTypesToClear[del.id] = true;
                    k[n] = del.id;
                    n = n + 1;

                }
            } catch (e) {
            }
        });


        if (k.length > 0) {
            createNotification("Deleted", k.join(',') + " were deleted", "deleteCookiesNotification");
        } else {
            return 0;
        }

        var a = new Date().getTime();
        var b = 1000 * 60 * 60 * parseInt(res["timeInterval"]);
        var c = a - b;

        chrome.browsingData.remove({
            "since": c
        },
                dataTypesToClear
                , () => {

        });

    });
}




chrome.webRequest.onAuthRequired.addListener(
        function (details, callbackFn) {
            console.log("onAuthRequired 1 ");
            loadOpt("proxiesList", async (res) => {

                proxy = res['selectedProxy'];
                p = proxy.split(":");
                console.log("onAuthRequired 2 " + proxy);
                if (p.length > 3) {
                    console.log("onAuthRequired 2 " + p[2] + " " + p[3]);
                    callbackFn({
                        authCredentials: {username: p[2], password: p[3]}
                    });
                }
            });
        },
        {urls: ["<all_urls>"]},
        ['asyncBlocking']
        );

