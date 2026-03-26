import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Effects 1.15

Item {
    id: root
    property var paletteMap
    property string productName: ""
    property real productVolume: 0
    property real productPrice: 0
    property string productImage: ""
    property color accentColor: "#ff6b35"
    property bool selected: false
    signal chosen()

    Rectangle {
        id: card
        anchors.fill: parent
        radius: 28
        color: Qt.rgba(1, 1, 1, root.selected ? 0.24 : 0.14)
        border.width: root.selected ? 2 : 1
        border.color: root.selected ? root.accentColor : Qt.rgba(1, 1, 1, 0.26)
        scale: root.selected ? 1.03 : mouseArea.containsMouse ? 1.015 : 1.0

        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.tint(root.paletteMap.panel, Qt.rgba(1, 1, 1, 0.08)) }
            GradientStop { position: 1.0; color: Qt.tint(root.paletteMap.panelAlt, Qt.rgba(0, 0, 0, 0.03)) }
        }

        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: Qt.rgba(0.04, 0.07, 0.14, root.selected ? 0.34 : 0.22)
            shadowVerticalOffset: root.selected ? 12 : 8
            shadowHorizontalOffset: 0
            shadowBlur: root.selected ? 1.0 : 0.7
        }

        Behavior on scale { NumberAnimation { duration: 150; easing.type: Easing.OutCubic } }

        Column {
            anchors.fill: parent
            anchors.margins: 18
            spacing: 10

            Row {
                width: parent.width
                Text {
                    text: root.productVolume.toFixed(root.productVolume >= 10 ? 0 : 1) + " L"
                    color: root.paletteMap.volume
                    font.pixelSize: 14
                    font.bold: true
                }
                Item { width: parent.width - volumeText.width - 2 }
                Text {
                    id: volumeText
                    visible: false
                }
            }

            Item {
                width: parent.width
                height: parent.height - 130
                Image {
                    anchors.centerIn: parent
                    source: root.productImage
                    sourceSize.width: 260
                    sourceSize.height: 220
                    fillMode: Image.PreserveAspectFit
                    smooth: true
                    y: -10
                }
            }

            Text {
                width: parent.width
                text: "$" + root.productPrice.toFixed(0)
                color: root.paletteMap.price
                font.pixelSize: 34
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
            }

            GlassButton {
                width: parent.width
                height: 44
                text: root.productName
                paletteMap: root.paletteMap
                emphasize: root.selected
                onClicked: root.chosen()
            }
        }

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.margins: 10
            height: 6
            radius: 3
            color: root.accentColor
            opacity: root.selected ? 0.88 : 0.32
        }
    }

    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: root.chosen()
    }
}
