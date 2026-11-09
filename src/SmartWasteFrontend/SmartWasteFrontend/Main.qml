import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Shapes

ApplicationWindow {
    id: root
    visible: true
    width: 1300
    height: 840
    minimumWidth: 1050
    minimumHeight: 720
    title: "Smart Waste - AI Sorting Assistant"
    color: "#080D0B"

    // ---------- STATE ----------
    property string mode: "live"            // live | analyzing | result
    property string systemStatus: "Live feed"
    property string activeBin: ""           // "", food, recyclable, paper, garbage
    property real confidence: 0
    property real shownConfidence: 0
    property string tip: ""
    property int daysOnline: 0

    // Stats and earned badges come from the API (which reads the database)
    property var stats: ({ "scanned": 0, "recycled": 0, "composted": 0, "garbage": 0, "days": 0 })
    property var earned: []
    property bool statsLoaded: false

    Behavior on shownConfidence {
        NumberAnimation { duration: 1400; easing.type: Easing.OutCubic }
    }

    // ---------- BADGES ----------
    // Images live in badges/<id>.png. Draw your own and overwrite badge1.png ... badge8.png.
    // The ids and goals here must match BADGE_RULES in database.py.
    readonly property var badgeDefs: [
        { "id": "badge1", "title": "First scan",        "desc": "Scan 1 item",          "stat": "scanned",   "goal": 1 },
        { "id": "badge2", "title": "Getting going",     "desc": "Scan 5 items",         "stat": "scanned",   "goal": 5 },
        { "id": "badge3", "title": "Sorting pro",       "desc": "Scan 25 items",        "stat": "scanned",   "goal": 25 },
        { "id": "badge4", "title": "First recycle",     "desc": "Recycle 1 item",       "stat": "recycled",  "goal": 1 },
        { "id": "badge5", "title": "Recycling regular", "desc": "Recycle 10 items",     "stat": "recycled",  "goal": 10 },
        { "id": "badge6", "title": "Compost starter",   "desc": "Compost 1 food item",  "stat": "composted", "goal": 1 },
        { "id": "badge7", "title": "One day online",    "desc": "Stay online for 1 day", "stat": "days",     "goal": 1 },
        { "id": "badge8", "title": "One week online",   "desc": "Stay online for 7 days", "stat": "days",    "goal": 7 }
    ]

    readonly property int badgeCount: earned.length

    // Called every time the backend pushes new stats (JSON text)
    function applyStats(json) {
        var s
        try { s = JSON.parse(json) } catch (e) { return }

        // no toast for badges that were already earned before the app opened
        var fresh = []
        if (statsLoaded) {
            for (var i = 0; i < badgeDefs.length; i++) {
                var d = badgeDefs[i]
                if (s.earned.indexOf(d.id) >= 0 && earned.indexOf(d.id) < 0) fresh.push(d)
            }
        }

        stats = s
        earned = s.earned
        daysOnline = s.days
        statsLoaded = true

        if (fresh.length > 0) {
            toast.badgeId = fresh[0].id
            toast.text = fresh.length > 1 ? fresh.length + " new badges unlocked" : "Badge unlocked: " + fresh[0].title
            toastAnim.restart()
        }
    }

    // ---------- CONTENT PER BIN ----------
    // "guide": picture shown in the info screen (path relative to this file, which is one folder
    // below the project root, so we go up with ../). If it is missing, a list is shown instead.
    readonly property var binInfo: ({
        "food": {
            "short": "Food scraps", "card": "#0F8A43", "glow": "#2BE08A", "guide": "../guides/food.png",
            "tip": "Remove stickers and packaging first.",
            "accepted": ["Fruit and vegetable scraps", "Coffee grounds", "Tea bags", "Eggshells",
                         "Bread and grains", "Meat and bones", "Food-soiled paper"],
            "avoid": ["Plastic packaging", "Liquids", "Cutlery"],
            "facts": [
                "Food rotting in a landfill releases methane, a greenhouse gas far stronger than CO2.",
                "Roughly a third of all food produced is never eaten.",
                "Composted scraps turn into nutrient-rich soil in a few months.",
                "Compost helps soil hold water, so gardens can need less watering.",
                "Coffee grounds and eggshells are favourites of compost piles."
            ]
        },
        "recyclable": {
            "short": "Recycling", "card": "#5F6064", "glow": "#C4C9D0", "guide": "../guides/recyclable.png",
            "tip": "Empty any liquid before placing it in the bin.",
            "accepted": ["Plastic containers", "Metal cans", "Glass bottles and jars", "Cartons",
                         "Cups and lids (no sleeves)"],
            "avoid": ["Cup sleeves", "Plastic film and bags", "Styrofoam", "Greasy takeout containers"],
            "facts": [
                "Aluminum can be recycled over and over with no loss in quality.",
                "Recycling aluminum uses about 95% less energy than making it from raw ore.",
                "A quick rinse keeps a whole batch of recycling from being rejected.",
                "Glass can be recycled endlessly without losing quality."
            ]
        },
        "paper": {
            "short": "Paper", "card": "#0A5A9E", "glow": "#4DA6FF", "guide": "../guides/paper.png",
            "tip": "Keep it dry and free of food.",
            "accepted": ["Newspaper", "Office paper", "Mail and flyers", "Flattened cardboard", "Paper bags"],
            "avoid": ["Greasy or wet paper", "Tissues and napkins", "Wax-coated paper"],
            "facts": [
                "Paper fibers can be recycled several times before they wear out.",
                "Greasy pizza boxes can't go in paper recycling: oil ruins the pulp.",
                "Recycling paper uses far less energy than making it from fresh wood.",
                "Bagging shredded paper stops loose bits slipping through sorting machines."
            ]
        },
        "garbage": {
            "short": "Garbage", "card": "#1B201E", "glow": "#E8ECEA", "guide": "../guides/garbage.png",
            "tip": "When unsure, bin it. Don't contaminate recycling.",
            "accepted": ["Chip bags and wrappers", "Plastic film", "Styrofoam", "Broken ceramics",
                         "Cup sleeves", "Diapers"],
            "avoid": ["Food scraps", "Bottles and cans", "Clean paper"],
            "facts": [
                "Chip bags and snack wrappers mix plastic and foil, so they can't be recycled.",
                "Broken ceramics and mirrors melt at different temperatures than glass bottles.",
                "Soiled tissues have fibers too short to recycle.",
                "One wrong item in recycling can spoil a whole load."
            ]
        }
    })

    // Maps whatever string the backend sends as "bin" to one of: food, recyclable, paper, garbage
    function binKey(name) {
        var n = String(name).toLowerCase()
        if (n.indexOf("food") >= 0 || n.indexOf("compost") >= 0 || n.indexOf("organic") >= 0) return "food"
        if (n.indexOf("paper") >= 0 || n.indexOf("cardboard") >= 0) return "paper"
        if (n.indexOf("recycl") >= 0 || n.indexOf("container") >= 0) return "recyclable"
        return "garbage"
    }

    function certaintyLabel(c) {
        return c >= 0.85 ? "High certainty" : (c >= 0.6 ? "Medium certainty" : "Low certainty")
    }

    function showResult(category, conf) {
        var info = binInfo[category]
        if (!info) return
        activeBin = category
        confidence = conf
        shownConfidence = conf
        tip = info.tip
        mode = "result"
        // scan counts and badges are handled by the database now (see applyStats)
    }

    function resetToLive() {
        infoOverlay.close()
        activeBin = ""
        shownConfidence = 0
        tip = ""
        mode = "live"
    }

    // ---------- REUSABLE COMPONENTS ----------
    component ActionButton: Rectangle {
        id: btn
        property string label
        property bool primary: true
        property bool enabledState: true
        signal clicked()

        implicitHeight: 42
        implicitWidth: btnText.implicitWidth + 40
        radius: 12
        color: primary ? (enabledState ? "#16D982" : "#26302B") : "#CC0C120F"
        border.color: primary ? "transparent" : "#35423B"
        opacity: enabledState ? 1 : 0.55

        Text {
            id: btnText
            anchors.centerIn: parent
            text: btn.label
            font.pixelSize: 14
            font.bold: true
            color: btn.primary ? "#06140D" : "#D8E0DB"
        }
        MouseArea {
            id: ma
            anchors.fill: parent
            enabled: btn.enabledState
            cursorShape: Qt.PointingHandCursor
            onClicked: btn.clicked()
        }
        scale: ma.pressed ? 0.96 : 1
        Behavior on scale { NumberAnimation { duration: 90 } }
    }

    component Chip: Rectangle {
        id: chip
        property string label
        property color fill: "#EAF0EC"
        property color ink: "#1B2420"
        width: chipText.implicitWidth + 22
        height: 32
        radius: 16
        color: fill
        Text { id: chipText; anchors.centerIn: parent; text: chip.label; color: chip.ink; font.pixelSize: 13 }
    }

    component BadgeSlot: Item {
        id: slot
        property string badgeId
        property string title
        property string desc
        property bool unlocked: false
        width: 46
        height: 46

        Shape {
            anchors.fill: parent
            opacity: slot.unlocked ? 0 : 1
            layer.enabled: true
            layer.samples: 4
            Behavior on opacity { NumberAnimation { duration: 300 } }
            ShapePath {
                strokeColor: "#4A574F"
                strokeWidth: 2
                fillColor: "transparent"
                strokeStyle: ShapePath.DashLine
                dashPattern: [3, 3]
                PathAngleArc { centerX: 23; centerY: 23; radiusX: 21; radiusY: 21; startAngle: 0; sweepAngle: 360 }
            }
        }
        Image {
            anchors.fill: parent
            anchors.margins: 1
            source: "../badges/" + slot.badgeId + ".png"
            fillMode: Image.PreserveAspectFit
            mipmap: true
            opacity: slot.unlocked ? 1 : 0
            scale: slot.unlocked ? 1 : 0.4
            Behavior on opacity { NumberAnimation { duration: 300 } }
            Behavior on scale { NumberAnimation { duration: 600; easing.type: Easing.OutBack; easing.overshoot: 2 } }
        }
        HoverHandler { id: hov }
        ToolTip.visible: hov.hovered
        ToolTip.delay: 250
        ToolTip.text: slot.unlocked ? slot.title + ": " + slot.desc : "Locked: " + slot.desc
    }

    component Flower: Item {
        id: fl
        property color petal: "white"
        property bool open: false
        width: 16
        height: 20
        scale: open ? 1 : 0
        transformOrigin: Item.Bottom
        Behavior on scale { NumberAnimation { duration: 450; easing.type: Easing.OutBack; easing.overshoot: 2.5 } }

        Rectangle { width: 2; height: 9; color: "#2F7A17"; anchors.horizontalCenter: parent.horizontalCenter; anchors.bottom: parent.bottom }
        Item {
            width: 14; height: 14
            anchors.horizontalCenter: parent.horizontalCenter
            Repeater {
                model: 5
                Rectangle {
                    width: 6; height: 6; radius: 3
                    color: fl.petal
                    x: 4 + 4.5 * Math.cos(index * 2 * Math.PI / 5)
                    y: 4 + 4.5 * Math.sin(index * 2 * Math.PI / 5)
                }
            }
            Rectangle { x: 4; y: 4; width: 6; height: 6; radius: 3; color: "#F5C518" }
        }
    }

    // Plants vs Zombies style loading bar
    component PvzBar: Item {
        id: pvz
        property real value: 0
        readonly property real fillW: Math.max(0, Math.min(1, value)) * (width - 16)
        implicitHeight: 36
        onFillWChanged: grass.requestPaint()
        onWidthChanged: grass.requestPaint()

        Rectangle {
            y: 14
            width: parent.width
            height: 20
            radius: 10
            color: "#5B3A1C"
            border.color: "#2E1C0C"
            border.width: 2
        }

        Canvas {
            id: grass
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                if (pvz.fillW < 1) return
                var x0 = 8, top = 15, bot = 31
                var w = x0 + pvz.fillW
                ctx.beginPath()
                ctx.moveTo(x0, bot)
                ctx.lineTo(x0, top)
                var i = 0
                for (var x = x0; x < w; x += 6) {
                    ctx.lineTo(Math.min(x + 3, w), top - 4 - (i % 3) * 1.5)
                    ctx.lineTo(Math.min(x + 6, w), top)
                    i++
                }
                ctx.lineTo(w, bot)
                ctx.closePath()
                var g = ctx.createLinearGradient(0, top - 8, 0, bot)
                g.addColorStop(0, "#8EE23C")
                g.addColorStop(0.4, "#5DB52A")
                g.addColorStop(1, "#2F7A17")
                ctx.fillStyle = g
                ctx.fill()
            }
        }

        Repeater {
            model: [
                { "p": 0.13, "c": "#FFFFFF" },
                { "p": 0.43, "c": "#FF9EC4" },
                { "p": 0.76, "c": "#FFFFFF" }
            ]
            Flower {
                x: 8 + modelData.p * (pvz.width - 16) - width / 2
                y: -3
                petal: modelData.c
                open: pvz.value >= modelData.p
            }
        }

        Item {
            width: 30
            height: 30
            x: 8 + pvz.fillW - 15
            y: 1
            rotation: pvz.fillW * 3
            Rectangle { anchors.fill: parent; radius: 15; color: "#3F8F1E"; border.color: "#256012"; border.width: 2 }
            Rectangle { anchors.centerIn: parent; width: 20; height: 20; radius: 10; color: "#62B52B"; border.color: "#2F7A17" }
            Rectangle { anchors.centerIn: parent; width: 9; height: 9; radius: 5; color: "#8EE23C" }
            Rectangle { x: 13.5; y: 2; width: 3; height: 8; color: "#256012" }
        }
    }

    // A bin whose lid morphs into a round button that floats above it when it is the answer
    component BinCard: Item {
        id: bin
        property string label
        property color bodyColor
        property color lidColor
        property color glow
        property string openingShape: "ellipse"   // ellipse | slot | square
        property bool active: false
        property bool dimmed: false
        property alias lidItem: lid
        signal lidClicked()

        z: active ? 10 : 0
        opacity: dimmed ? 0.4 : 1
        scale: active ? 1.08 : 1
        Behavior on opacity { NumberAnimation { duration: 350 } }
        Behavior on scale { NumberAnimation { duration: 500; easing.type: Easing.OutBack } }

        Rectangle {
            anchors.fill: body
            anchors.margins: -9
            radius: 24
            color: bin.glow
            opacity: bin.active ? 0.2 : 0
            Behavior on opacity { NumberAnimation { duration: 500 } }
        }

        Rectangle {
            id: body
            anchors.fill: parent
            radius: 16
            color: bin.bodyColor
            border.width: 2
            border.color: bin.active ? bin.glow : Qt.lighter(bin.bodyColor, 1.3)
            Behavior on border.color { ColorAnimation { duration: 300 } }

            Rectangle {
                id: cavity
                x: 8; y: 8
                width: parent.width - 16
                height: parent.height * 0.42
                radius: 9
                color: "#040605"
                Rectangle {
                    anchors.fill: parent
                    radius: 9
                    color: bin.glow
                    opacity: bin.active ? 0.3 : 0
                    Behavior on opacity { NumberAnimation { duration: 600 } }
                }
            }

            Text {
                anchors.top: cavity.bottom
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 8
                text: bin.label
                color: "white"
                font.bold: true
                font.pixelSize: 14
                fontSizeMode: Text.Fit
                minimumPixelSize: 10
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                wrapMode: Text.Wrap
            }
        }

        // pulsing ring that asks for a click
        Rectangle {
            id: ring
            width: 64; height: 64; radius: 32
            x: lid.x + lid.width / 2 - 32
            y: lid.y + lid.height / 2 - 32
            color: "transparent"
            border.color: bin.glow
            border.width: 3
            opacity: 0
            visible: bin.active
            ParallelAnimation {
                running: bin.active
                loops: Animation.Infinite
                NumberAnimation { target: ring; property: "scale"; from: 1; to: 1.7; duration: 1200 }
                NumberAnimation { target: ring; property: "opacity"; from: 0.8; to: 0; duration: 1200 }
            }
        }

        Rectangle {
            id: lid
            property real o: bin.active ? 1 : 0          // 0 = closed on the bin, 1 = floating above
            property real bob: 0
            readonly property real c: Math.max(0, Math.min(1, o))
            readonly property real dia: 64
            Behavior on o { NumberAnimation { duration: 800; easing.type: Easing.OutBack; easing.overshoot: 1.4 } }

            width: (bin.width - 16) + (dia - (bin.width - 16)) * o
            height: cavity.height + (dia - cavity.height) * o
            x: (bin.width - width) / 2
            y: 8 + (-dia - 26) * o + bob
            radius: 9 + (Math.min(width, height) / 2 - 9) * c
            color: bin.lidColor
            border.width: bin.active ? 2 : 1
            border.color: bin.active ? bin.glow : Qt.lighter(bin.lidColor, 1.2)

            SequentialAnimation on bob {
                running: bin.active
                loops: Animation.Infinite
                NumberAnimation { to: -7; duration: 700; easing.type: Easing.InOutSine }
                NumberAnimation { to: 0; duration: 700; easing.type: Easing.InOutSine }
            }
            Connections {
                target: bin
                function onActiveChanged() { if (!bin.active) lid.bob = 0 }
            }

            // opening shape on the closed lid
            Rectangle {
                anchors.centerIn: parent
                opacity: 1 - lid.c
                width: bin.openingShape === "slot" ? parent.width * 0.55
                     : bin.openingShape === "square" ? parent.height * 0.6
                     : parent.width * 0.6
                height: bin.openingShape === "slot" ? 10
                      : bin.openingShape === "square" ? parent.height * 0.6
                      : parent.height * 0.4
                radius: bin.openingShape === "ellipse" ? height / 2 : 3
                color: Qt.darker(bin.lidColor, 1.35)
            }
            Text {
                anchors.centerIn: parent
                text: "i"
                opacity: lid.c
                color: "white"
                font.bold: true
                font.pixelSize: 30
            }

            MouseArea {
                anchors.fill: parent
                enabled: bin.active
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: bin.lidClicked()
            }
        }

        Rectangle {
            x: (bin.width - width) / 2
            y: lid.y - 32
            width: tapText.implicitWidth + 22
            height: 24
            radius: 12
            color: "#EE0A0F0D"
            border.color: bin.glow
            opacity: lid.c
            visible: bin.active
            Text { id: tapText; anchors.centerIn: parent; text: "Tap to learn more"; color: "white"; font.pixelSize: 11; font.bold: true }
        }
    }

    // ---------- LAYOUT ----------
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 22
        spacing: 16

        // HEADER: title, badge collection, stats
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 70
            radius: 16
            color: "#111A15"
            border.color: "#202A23"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 18
                anchors.rightMargin: 14
                spacing: 12

                Rectangle {
                    width: 36; height: 36; radius: 11
                    color: "#16D982"
                    Text { anchors.centerIn: parent; text: "♻"; font.pixelSize: 23; color: "#071A10" }
                }
                Column {
                    spacing: 1
                    Text { text: "Smart Waste"; color: "white"; font.bold: true; font.pixelSize: 19 }
                    Text { text: "AI sorting assistant"; color: "#8C9A90"; font.pixelSize: 12 }
                }

                Item { Layout.fillWidth: true }

                Row {
                    spacing: 8
                    Repeater {
                        model: root.badgeDefs
                        BadgeSlot {
                            badgeId: modelData.id
                            title: modelData.title
                            desc: modelData.desc
                            unlocked: root.earned.indexOf(modelData.id) >= 0
                        }
                    }
                }

                ActionButton {
                    id: statsBtn
                    label: "Stats"
                    primary: false
                    onClicked: statsPopup.opened ? statsPopup.close() : statsPopup.open()
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 18

            // ===== LEFT: CAMERA =====
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 420
                radius: 22
                color: "#111714"
                border.color: "#202A23"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 8
                        Rectangle {
                            width: 9; height: 9; radius: 5
                            color: !videoArea.hasVideo ? "#6F7C74"
                                 : root.mode === "analyzing" ? "#F5B83D" : "#16D982"
                        }
                        Text {
                            text: videoArea.hasVideo ? "Camera on" : "Waiting for camera"
                            color: "#E5EAE6"
                            font.pixelSize: 13
                            font.bold: true
                        }
                        Item { Layout.fillWidth: true }
                        Text { text: root.systemStatus; color: "#849188"; font.pixelSize: 12 }
                    }

                    Text {
                        text: "Live waste detection"
                        color: "#B0B9B2"
                        font.pixelSize: 16
                        font.bold: true
                    }

                    Rectangle {
                        id: videoArea
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 18
                        color: "#060A08"
                        clip: true
                        border.width: 2
                        border.color: root.mode === "analyzing" ? "#F5B83D"
                                    : root.activeBin !== "" ? root.binInfo[root.activeBin].glow : "#1B241F"
                        Behavior on border.color { ColorAnimation { duration: 300 } }

                        property int frameNumber: 0
                        property bool nextIsA: true
                        property bool shownIsA: true
                        property bool hasVideo: false

                        Image {
                            id: frameA
                            anchors.fill: parent
                            fillMode: Image.PreserveAspectCrop   // fills the box; use PreserveAspectFit to see the whole frame
                            cache: false
                            asynchronous: true
                            visible: videoArea.shownIsA
                            onStatusChanged: {
                                if (status === Image.Ready) {
                                    videoArea.shownIsA = true
                                    videoArea.hasVideo = true
                                } else if (status === Image.Error) {
                                    videoArea.hasVideo = false
                                }
                            }
                        }
                        Image {
                            id: frameB
                            anchors.fill: parent
                            fillMode: Image.PreserveAspectCrop   // fills the box; use PreserveAspectFit to see the whole frame
                            cache: false
                            asynchronous: true
                            visible: !videoArea.shownIsA
                            onStatusChanged: {
                                if (status === Image.Ready) {
                                    videoArea.shownIsA = false
                                    videoArea.hasVideo = true
                                } else if (status === Image.Error) {
                                    videoArea.hasVideo = false
                                }
                            }
                        }

                        // asks the API for a new frame about 10 times a second
                        Timer {
                            interval: 100
                            running: true
                            repeat: true
                            onTriggered: {
                                videoArea.frameNumber++
                                var url = backend.apiBase + "/camera/frame?t=" + videoArea.frameNumber
                                if (videoArea.nextIsA)
                                    frameA.source = url
                                else
                                    frameB.source = url
                                videoArea.nextIsA = !videoArea.nextIsA
                            }
                        }

                        Column {
                            visible: !videoArea.hasVideo
                            anchors.centerIn: parent
                            spacing: 10
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: "◉"; color: "#4A574F"; font.pixelSize: 44 }
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: "Camera feed will appear here"; color: "#E5EAE6"; font.pixelSize: 16; font.bold: true }
                            Text { anchors.horizontalCenter: parent.horizontalCenter; text: "Waiting for video connection"; color: "#6F7C74"; font.pixelSize: 12 }
                        }

                        Rectangle {
                            width: parent.width
                            height: 3
                            color: "#F5B83D"
                            visible: root.mode === "analyzing"
                            opacity: 0.85
                            SequentialAnimation on y {
                                running: root.mode === "analyzing"
                                loops: Animation.Infinite
                                NumberAnimation { from: 0; to: videoArea.height - 3; duration: 900; easing.type: Easing.InOutSine }
                                NumberAnimation { from: videoArea.height - 3; to: 0; duration: 900; easing.type: Easing.InOutSine }
                            }
                        }

                        Row {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 16
                            spacing: 12
                            z: 3

                            ActionButton {
                                label: "Pause and analyze"
                                enabledState: root.mode === "live"
                                onClicked: {
                                    root.mode = "analyzing"
                                    backend.pause()
                                }
                            }
                            ActionButton {
                                label: "Resume feed"
                                primary: false
                                enabledState: root.mode !== "live"
                                onClicked: {
                                    root.resetToLive()
                                    backend.resume()
                                }
                            }
                        }
                    }
                }
            }

            // ===== RIGHT: CONFIDENCE, RESULT, BINS =====
            ColumnLayout {
                Layout.fillHeight: true
                Layout.preferredWidth: Math.max(440, root.width * 0.38)
                spacing: 18

                // CONFIDENCE
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 92
                    radius: 18
                    color: "#111714"
                    border.color: "#202A23"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 6

                        RowLayout {
                            Layout.fillWidth: true
                            Text { text: "Confidence"; color: "white"; font.bold: true; font.pixelSize: 16 }
                            Item { Layout.fillWidth: true }
                            Text {
                                text: root.activeBin === "" ? "Waiting for a scan"
                                    : root.certaintyLabel(root.confidence) + "  " + Math.round(root.shownConfidence * 100) + "%"
                                color: "#B7C2BB"
                                font.pixelSize: 13
                            }
                        }
                        PvzBar {
                            Layout.fillWidth: true
                            value: root.shownConfidence
                        }
                    }
                }

                // RESULT
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 150
                    radius: 20
                    color: root.activeBin === "" ? "#18201B" : root.binInfo[root.activeBin].card
                    Behavior on color { ColorAnimation { duration: 400 } }

                    Column {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: 22
                        spacing: 8

                        Text {
                            width: parent.width
                            text: root.activeBin === "" ? "Ready to sort" : "Place item in " + root.binInfo[root.activeBin].short
                            color: "white"
                            font.bold: true
                            font.pixelSize: 26
                            elide: Text.ElideRight
                        }
                        Text {
                            width: parent.width
                            text: root.activeBin === ""
                                  ? "Pause the feed on an item and the matching bin will open."
                                  : root.tip
                            color: "#E3EAE5"
                            font.pixelSize: 15
                            wrapMode: Text.Wrap
                        }
                    }
                }

                // BINS
                RowLayout {
                    id: binRow
                    Layout.fillWidth: true
                    Layout.fillHeight: false
                    Layout.preferredHeight: 190
                    Layout.minimumHeight: 190
                    Layout.maximumHeight: 190
                    spacing: 12

                    BinCard {
                        id: binFood
                        Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 100
                        label: "Food scraps"
                        bodyColor: "#12A150"; lidColor: "#17B35A"; glow: "#2BE08A"
                        openingShape: "ellipse"
                        active: root.activeBin === "food"
                        dimmed: root.activeBin !== "" && !active
                        onLidClicked: infoOverlay.openFrom(lidItem, "food", lidColor)
                    }
                    BinCard {
                        id: binRecyc
                        Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 100
                        label: "Recyclable containers"
                        bodyColor: "#808185"; lidColor: "#8D8E93"; glow: "#C4C9D0"
                        openingShape: "ellipse"
                        active: root.activeBin === "recyclable"
                        dimmed: root.activeBin !== "" && !active
                        onLidClicked: infoOverlay.openFrom(lidItem, "recyclable", lidColor)
                    }
                    BinCard {
                        id: binPaper
                        Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 100
                        label: "Paper"
                        bodyColor: "#08508A"; lidColor: "#0B5D9F"; glow: "#4DA6FF"
                        openingShape: "slot"
                        active: root.activeBin === "paper"
                        dimmed: root.activeBin !== "" && !active
                        onLidClicked: infoOverlay.openFrom(lidItem, "paper", lidColor)
                    }
                    BinCard {
                        id: binGarb
                        Layout.fillWidth: true; Layout.fillHeight: true; Layout.preferredWidth: 100
                        label: "Garbage"
                        bodyColor: "#171A19"; lidColor: "#1F2321"; glow: "#E8ECEA"
                        openingShape: "square"
                        active: root.activeBin === "garbage"
                        dimmed: root.activeBin !== "" && !active
                        onLidClicked: infoOverlay.openFrom(lidItem, "garbage", lidColor)
                    }
                }
            }
        }
    }

    // ---------- STATS POPUP ----------
    Popup {
        id: statsPopup
        parent: Overlay.overlay
        x: root.width - width - 22
        y: 22 + 70 + 8
        width: 340
        padding: 18
        closePolicy: Popup.CloseOnPressOutside | Popup.CloseOnEscape
        enter: Transition { NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 150 } }
        exit: Transition { NumberAnimation { property: "opacity"; from: 1; to: 0; duration: 120 } }
        background: Rectangle { radius: 18; color: "#111A15"; border.color: "#2A362F" }

        contentItem: Column {
            spacing: 10

            Text { text: "Your stats"; color: "white"; font.bold: true; font.pixelSize: 18 }

            Repeater {
                model: [
                    { "l": "Items scanned", "v": root.stats.scanned },
                    { "l": "Items recycled", "v": root.stats.recycled },
                    { "l": "Food scraps composted", "v": root.stats.composted },
                    { "l": "Sent to garbage", "v": root.stats.garbage },
                    { "l": "Days online", "v": root.daysOnline },
                    { "l": "Badges earned", "v": root.badgeCount + " / " + root.badgeDefs.length }
                ]
                Row {
                    width: statsPopup.availableWidth
                    Text { width: parent.width - valueText.implicitWidth; text: modelData.l; color: "#AAB5AD"; font.pixelSize: 14 }
                    Text { id: valueText; text: modelData.v; color: "white"; font.bold: true; font.pixelSize: 14 }
                }
            }

            Rectangle { width: parent.width; height: 1; color: "#26302B" }

            Text {
                text: "Reset progress"
                color: "#8C9A90"
                font.pixelSize: 12
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: backend.resetProgress()
                }
            }
        }
    }

    // ---------- BADGE TOAST ----------
    Rectangle {
        id: toast
        property string text: ""
        property string badgeId: "badge1"
        z: 150
        width: toastRow.implicitWidth + 36
        height: 56
        radius: 28
        color: "#EE111A15"
        border.color: "#16D982"
        x: (root.width - width) / 2
        y: -height - 10
        opacity: 0

        Row {
            id: toastRow
            anchors.centerIn: parent
            spacing: 10
            Image { width: 38; height: 38; source: "../badges/" + toast.badgeId + ".png"; fillMode: Image.PreserveAspectFit; mipmap: true }
            Text { anchors.verticalCenter: parent.verticalCenter; text: toast.text; color: "white"; font.bold: true; font.pixelSize: 14 }
        }
    }
    SequentialAnimation {
        id: toastAnim
        ParallelAnimation {
            NumberAnimation { target: toast; property: "y"; to: 22 + 70 + 12; duration: 450; easing.type: Easing.OutBack }
            NumberAnimation { target: toast; property: "opacity"; to: 1; duration: 250 }
        }
        PauseAnimation { duration: 3000 }
        ParallelAnimation {
            NumberAnimation { target: toast; property: "y"; to: -toast.height - 10; duration: 350 }
            NumberAnimation { target: toast; property: "opacity"; to: 0; duration: 350 }
        }
    }

    // ---------- FULL-SCREEN INFO (zooms out of the lid) ----------
    Item {
        id: infoOverlay
        anchors.fill: parent
        z: 100
        visible: t > 0
        focus: visible
        Keys.onEscapePressed: close()

        property real t: 0
        property real sx: 0
        property real sy: 0
        property real sw: 64
        property real sh: 64
        property color startColor: "#808185"
        property string cat: ""
        property int factIdx: -1
        property string shownFact: ""
        readonly property var info: cat === "" ? null : root.binInfo[cat]

        function openFrom(item, category, lidColor) {
            var a = item.mapToItem(infoOverlay, 0, 0)
            var b = item.mapToItem(infoOverlay, item.width, item.height)
            sx = a.x; sy = a.y; sw = b.x - a.x; sh = b.y - a.y
            startColor = lidColor
            cat = category
            factIdx = -1
            pickFact(true)
            zoomAnim.stop()
            zoomAnim.to = 1
            zoomAnim.start()
        }

        function close() {
            if (t <= 0) return
            zoomAnim.stop()
            zoomAnim.to = 0
            zoomAnim.start()
        }

        function pickFact(instant) {
            if (!info) return
            var n = info.facts.length
            var i = Math.floor(Math.random() * n)
            if (n > 1 && i === factIdx) i = (i + 1) % n
            factIdx = i
            if (instant) shownFact = info.facts[i]
            else factSwap.restart()
        }

        NumberAnimation { id: zoomAnim; target: infoOverlay; property: "t"; duration: 560; easing.type: Easing.InOutCubic }

        Rectangle {
            anchors.fill: parent
            color: "black"
            opacity: 0.7 * infoOverlay.t
            MouseArea { anchors.fill: parent; enabled: infoOverlay.t > 0.9; onClicked: infoOverlay.close() }
        }

        Rectangle {
            id: zoomCard
            readonly property real t: infoOverlay.t
            readonly property color endColor: infoOverlay.info ? infoOverlay.info.card : "#111111"
            x: infoOverlay.sx + (28 - infoOverlay.sx) * t
            y: infoOverlay.sy + (28 - infoOverlay.sy) * t
            width: infoOverlay.sw + (infoOverlay.width - 56 - infoOverlay.sw) * t
            height: infoOverlay.sh + (infoOverlay.height - 56 - infoOverlay.sh) * t
            radius: Math.min(width, height) / 2 * (1 - t) + 26 * t
            color: Qt.rgba(infoOverlay.startColor.r + (endColor.r - infoOverlay.startColor.r) * t,
                           infoOverlay.startColor.g + (endColor.g - infoOverlay.startColor.g) * t,
                           infoOverlay.startColor.b + (endColor.b - infoOverlay.startColor.b) * t, 1)
            border.width: 2
            border.color: infoOverlay.info ? infoOverlay.info.glow : "transparent"
            clip: true
            MouseArea { anchors.fill: parent }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 26
                spacing: 16
                visible: infoOverlay.t > 0.5
                opacity: Math.max(0, (infoOverlay.t - 0.6) / 0.4)

                RowLayout {
                    Layout.fillWidth: true
                    Column {
                        Layout.fillWidth: true
                        spacing: 4
                        Text {
                            text: infoOverlay.info ? "Place it in " + infoOverlay.info.short : ""
                            color: "white"; font.bold: true; font.pixelSize: 32
                        }
                        Text {
                            text: infoOverlay.info ? infoOverlay.info.tip : ""
                            color: "#E3EAE5"; font.pixelSize: 15
                        }
                    }
                    Rectangle {
                        width: 42; height: 42; radius: 21
                        color: "#33000000"
                        Text { anchors.centerIn: parent; text: "✕"; color: "white"; font.pixelSize: 18 }
                        MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: infoOverlay.close() }
                    }
                }

                // fun fact row
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 108
                    radius: 18
                    color: "#26FFFFFF"

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 18

                        Column {
                            Layout.fillWidth: true
                            spacing: 4
                            Text {
                                text: "Did you know?"
                                color: infoOverlay.info ? infoOverlay.info.glow : "white"
                                font.bold: true
                                font.pixelSize: 13
                            }
                            Text {
                                id: factText
                                width: parent.width
                                text: infoOverlay.shownFact
                                color: "white"
                                font.pixelSize: 20
                                wrapMode: Text.Wrap
                            }
                        }
                        ActionButton {
                            label: "Another fact"
                            primary: false
                            onClicked: infoOverlay.pickFact(false)
                        }
                    }
                }

                // bin guide (taller section)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 20
                    color: "white"
                    clip: true

                    Image {
                        id: guideImg
                        anchors.fill: parent
                        anchors.margins: 14
                        fillMode: Image.PreserveAspectFit
                        mipmap: true
                        source: infoOverlay.visible && infoOverlay.info ? infoOverlay.info.guide : ""
                        visible: status === Image.Ready
                    }

                    // shown until you add a guide picture
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 24
                        spacing: 12
                        visible: guideImg.status !== Image.Ready

                        Text { text: "What goes in this bin"; color: "#1B2420"; font.bold: true; font.pixelSize: 18 }
                        Flow {
                            Layout.fillWidth: true
                            spacing: 8
                            Repeater {
                                model: infoOverlay.info ? infoOverlay.info.accepted : []
                                Chip { label: modelData; fill: "#DDF3E6"; ink: "#14532D" }
                            }
                        }
                        Text { Layout.topMargin: 8; text: "Please leave out"; color: "#1B2420"; font.bold: true; font.pixelSize: 18 }
                        Flow {
                            Layout.fillWidth: true
                            spacing: 8
                            Repeater {
                                model: infoOverlay.info ? infoOverlay.info.avoid : []
                                Chip { label: modelData; fill: "#FBE0DD"; ink: "#7A1F14" }
                            }
                        }
                        Item { Layout.fillHeight: true }
                        Text {
                            text: infoOverlay.info ? "Add your guide picture at " + infoOverlay.info.guide : ""
                            color: "#7A857E"
                            font.pixelSize: 12
                        }
                    }
                }
            }
        }
    }

    SequentialAnimation {
        id: factSwap
        NumberAnimation { target: factText; property: "opacity"; to: 0; duration: 130 }
        ScriptAction { script: infoOverlay.shownFact = infoOverlay.info.facts[infoOverlay.factIdx] }
        NumberAnimation { target: factText; property: "opacity"; to: 1; duration: 300 }
    }

        // ---------- TEMP: manual test keys (delete when done) ----------
    Shortcut { sequence: "1"; onActivated: root.showResult("food", 0.95) }
    Shortcut { sequence: "2"; onActivated: root.showResult("recyclable", 0.72) }
    Shortcut { sequence: "3"; onActivated: root.showResult("paper", 0.55) }
    Shortcut { sequence: "4"; onActivated: root.showResult("garbage", 0.35) }
    Shortcut { sequence: "0"; onActivated: root.resetToLive() }
    Shortcut { sequence: "7"; onActivated: backend.setDemoDays(0) }   // reset time
    Shortcut { sequence: "8"; onActivated: backend.setDemoDays(1) }   // over 1 day
    Shortcut { sequence: "9"; onActivated: backend.setDemoDays(7) }   // over 7 days

    // ---------- BACKEND SIGNALS ----------
    Connections {
        target: backend

        function onStatusChanged(status) { root.systemStatus = status }
        function onResultChanged(item, bin, conf) {
            root.showResult(root.binKey(bin), conf)
        }
        function onStatsChanged(json) { root.applyStats(json) }
    }
}