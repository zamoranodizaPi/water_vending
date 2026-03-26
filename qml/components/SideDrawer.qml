import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Effects 1.15

Item {
    id: root
    property var paletteMap
    property bool open: false
    property string brandTitle: ""
    property string brandTagline: ""
    property string systemName: ""
    property string currentTheme: ""
    property string currentMode: ""
    signal closeRequested()
    signal toggleModeRequested()
    signal cycleThemeRequested()
    signal returnHomeRequested()

    x: open ? parent.width - width : parent.width + 24
    z: 30

    Behavior on x { NumberAnimation { duration: 260; easing.type: Easing.OutCubic } }

    Rectangle {
        anchors.fill: parent
        radius: 26
        color: Qt.rgba(1, 1, 1, currentMode === "light" ? 0.18 : 0.10)
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.20)
        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: Qt.rgba(0.04, 0.07, 0.14, 0.30)
            shadowVerticalOffset: 8
            shadowHorizontalOffset: -4
            shadowBlur: 0.8
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 22
            spacing: 14

            Text {
                text: root.brandTitle
                color: root.paletteMap.text
                font.pixelSize: 22
                font.bold: true
            }
            Text {
                text: root.brandTagline
                color: root.paletteMap.textSoft
                font.pixelSize: 12
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: Qt.rgba(1, 1, 1, 0.18)
            }

            Repeater {
                model: [
                    "Sistema: " + root.systemName,
                    "Tema: " + root.currentTheme,
                    "Modo: " + root.currentMode
                ]

                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 46
                    radius: 16
                    color: Qt.rgba(1, 1, 1, 0.08)
                    border.width: 1
                    border.color: Qt.rgba(1, 1, 1, 0.16)

                    Text {
                        anchors.centerIn: parent
                        text: modelData
                        color: root.paletteMap.text
                        font.pixelSize: 13
                    }
                }
            }

            Item { Layout.fillHeight: true }

            GlassButton {
                Layout.fillWidth: true
                text: "Cambiar tema"
                paletteMap: root.paletteMap
                onClicked: root.cycleThemeRequested()
            }
            GlassButton {
                Layout.fillWidth: true
                text: "Cambiar modo"
                paletteMap: root.paletteMap
                onClicked: root.toggleModeRequested()
            }
            GlassButton {
                Layout.fillWidth: true
                text: "Inicio"
                paletteMap: root.paletteMap
                secondary: true
                onClicked: root.returnHomeRequested()
            }
            GlassButton {
                Layout.fillWidth: true
                text: "Cerrar"
                paletteMap: root.paletteMap
                secondary: true
                onClicked: root.closeRequested()
            }
        }
    }
}
