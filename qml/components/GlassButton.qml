import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Effects 1.15

Button {
    id: root
    property var paletteMap
    property bool secondary: false
    property bool emphasize: false

    implicitHeight: 54

    background: Rectangle {
        id: bg
        radius: 18
        border.width: 1
        border.color: root.hovered ? Qt.rgba(1, 1, 1, 0.42) : Qt.rgba(1, 1, 1, 0.24)
        color: root.secondary ? Qt.rgba(1, 1, 1, 0.14) : "transparent"
        opacity: root.enabled ? 1 : 0.55
        scale: root.down ? 0.98 : root.hovered ? 1.03 : 1.0

        gradient: root.secondary ? undefined : Gradient {
            GradientStop { position: 0.0; color: root.paletteMap ? root.paletteMap.buttonGradient[0] : "#2563eb" }
            GradientStop { position: 0.5; color: root.paletteMap ? root.paletteMap.buttonGradient[1] : "#3b82f6" }
            GradientStop { position: 1.0; color: root.paletteMap ? root.paletteMap.buttonGradient[2] : "#06b6d4" }
        }

        layer.enabled: true
        layer.effect: MultiEffect {
            shadowEnabled: true
            shadowColor: Qt.rgba(0.05, 0.07, 0.14, root.hovered ? 0.34 : 0.24)
            shadowVerticalOffset: root.down ? 2 : 7
            shadowHorizontalOffset: 0
            shadowBlur: root.hovered ? 0.8 : 0.5
        }

        Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
        Behavior on opacity { NumberAnimation { duration: 160 } }

        Rectangle {
            anchors.fill: parent
            anchors.margins: 1
            radius: parent.radius - 1
            color: "transparent"
            border.width: root.emphasize ? 2 : 1
            border.color: Qt.rgba(1, 1, 1, root.hovered ? 0.30 : 0.16)
        }
    }

    contentItem: Text {
        text: root.text
        color: root.secondary ? (root.paletteMap ? root.paletteMap.text : "#111827") : (root.paletteMap ? root.paletteMap.buttonText : "white")
        font.pixelSize: 14
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
