
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 1250
    height: 800
    minimumWidth: 950
    minimumHeight: 650

    title: "Smart Waste - AI Sorting Assistant"
    color: "#080D0B"

    property string systemStatus: "System ready"
    property string detectedItem: "Aluminum can"
    property string recommendedBin: "Recycling"
    property real confidence: 0.94

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        // HEADER
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 65
            radius: 15
            color: "#111A15"
            border.color: "#202A23"

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16

                Rectangle {
                    width: 38
                    height: 38
                    radius: 11
                    color: "#16D982"

                    Text {
                        anchors.centerIn: parent
                        text: "♻"
                        font.pixelSize: 25
                        color: "#071A10"
                    }
                }

                Column {
                    spacing: 2

                    Text {
                        text: "Smart Waste"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 17
                    }

                    Text {
                        text: "AI sorting assistant"
                        color: "#8C9A90"
                        font.pixelSize: 11
                    }
                }

                Item { Layout.fillWidth: true }

                Text {
                    text: "●  " + systemStatus
                    color: "#16D982"
                    font.pixelSize: 12
                }
            }
        }

        // MAIN CONTENT
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 16

            // CAMERA PANEL
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.minimumWidth: 400
                radius: 22
                color: "#111714"
                border.color: "#202A23"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 18
                    spacing: 14

                    Text {
                        text: "CAMERA 01"
                        color: "#849188"
                        font.pixelSize: 11
                    }

                    Text {
                        text: "Live waste detection"
                        color: "white"
                        font.bold: true
                        font.pixelSize: 21
                    }

                    // VIDEO PLACEHOLDER
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 16
                        color: "#080D0B"

                        Column {
                            anchors.centerIn: parent
                            spacing: 12

                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "◉"
                                color: "#849188"
                                font.pixelSize: 42
                            }

                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "Camera feed will appear here"
                                color: "#E5EAE6"
                                font.pixelSize: 17
                                font.bold: true
                            }

                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: "Waiting for video connection"
                                color: "#849188"
                                font.pixelSize: 12
                            }
                        }
                    }

                    // CAMERA CONTROLS
                    RowLayout {
                        Layout.alignment: Qt.AlignHCenter
                        spacing: 12

                        Button {
                            text: "Ⅱ  Pause"
                            onClicked: backend.pause()
                        }

                        Button {
                            text: "▶  Resume"
                            onClicked: backend.resume()
                        }
                    }
                }
            }

            // CLASSIFICATION PANEL
            Rectangle {
                Layout.preferredWidth: 340
                Layout.fillHeight: true
                radius: 22
                color: "#111714"
                border.color: "#202A23"

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 20
                    spacing: 18

                    Text {
                        text: "Latest classification"
                        color: "#B0B9B2"
                        font.pixelSize: 14
                    }

                    Text {
                        text: "Detected item"
                        color: "#849188"
                        font.pixelSize: 12
                    }

                    Text {
                        text: detectedItem
                        color: "white"
                        font.bold: true
                        font.pixelSize: 25
                        wrapMode: Text.Wrap
                    }

                    // BIN RECOMMENDATION
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 165
                        radius: 17
                        color: "#1876F5"

                        Column {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: 18
                            spacing: 8

                            Text {
                                text: "Place item in"
                                color: "white"
                                font.pixelSize: 13
                            }

                            Text {
                                text: recommendedBin
                                color: "white"
                                font.bold: true
                                font.pixelSize: 29
                            }

                            Text {
                                text: "Blue bin"
                                color: "white"
                                font.pixelSize: 13
                            }

                            Rectangle {
                                width: parent.width
                                height: 1
                                color: "#669FFF"
                            }

                            Text {
                                text: "Empty any liquid before recycling."
                                color: "white"
                                font.pixelSize: 11
                                wrapMode: Text.Wrap
                            }
                        }
                    }

                    // CONFIDENCE
                    RowLayout {
                        Layout.fillWidth: true

                        Column {
                            spacing: 4

                            Text {
                                text: "Confidence"
                                color: "#AAB5AD"
                                font.pixelSize: 13
                            }

                            Text {
                                text: "Classification certainty"
                                color: "#849188"
                                font.pixelSize: 11
                            }
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: Math.round(confidence * 100) + "%"
                            color: "white"
                            font.bold: true
                            font.pixelSize: 30
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 9
                        radius: 5
                        color: "#28332D"

                        Rectangle {
                            width: parent.width *
                                   Math.max(0, Math.min(1, confidence))
                            height: parent.height
                            radius: 5
                            color: "#16D982"
                        }
                    }

                    Item { Layout.fillHeight: true }

                    // BOTTOM STATUS CARDS
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 75
                            radius: 13
                            color: "#1A211D"

                            Column {
                                anchors.centerIn: parent
                                spacing: 5

                                Text {
                                    text: "Response"
                                    color: "#849188"
                                    font.pixelSize: 11
                                }

                                Text {
                                    text: "42 ms"
                                    color: "white"
                                    font.bold: true
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 75
                            radius: 13
                            color: "#1A211D"

                            Column {
                                anchors.centerIn: parent
                                spacing: 5

                                Text {
                                    text: "Processing"
                                    color: "#849188"
                                    font.pixelSize: 11
                                }

                                Text {
                                    text: "On-device"
                                    color: "white"
                                    font.bold: true
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Connections {
        target: backend

        function onStatusChanged(status) {
            systemStatus = status
        }
    }
}
