import QtQuick 2.15

Rectangle {
    id: root
    property var paletteMap
    property bool animated: false

    gradient: Gradient {
        GradientStop { position: 0.0; color: root.paletteMap ? root.paletteMap.background[0] : "#1f2937" }
        GradientStop { position: 0.5; color: root.paletteMap ? root.paletteMap.background[1] : "#334155" }
        GradientStop { position: 1.0; color: root.paletteMap ? root.paletteMap.background[2] : "#475569" }
    }

    Rectangle {
        anchors.fill: parent
        color: "transparent"
        opacity: 0.18

        Canvas {
            anchors.fill: parent
            onPaint: {
                var ctx = getContext("2d")
                ctx.reset()
                ctx.strokeStyle = "rgba(255,255,255,0.10)"
                ctx.lineWidth = 1
                for (var x = 0; x < width; x += 48) {
                    ctx.beginPath()
                    ctx.moveTo(x, 0)
                    ctx.lineTo(x, height)
                    ctx.stroke()
                }
                for (var y = 0; y < height; y += 48) {
                    ctx.beginPath()
                    ctx.moveTo(0, y)
                    ctx.lineTo(width, y)
                    ctx.stroke()
                }
            }
        }
    }

    Rectangle {
        id: glowOne
        width: parent.width * 0.42
        height: width
        radius: width / 2
        x: -width * 0.15
        y: -height * 0.2
        color: Qt.rgba(1, 1, 1, 0.14)
        opacity: 0.9
        SequentialAnimation on x {
            running: root.animated
            loops: Animation.Infinite
            NumberAnimation { from: -glowOne.width * 0.15; to: root.width * 0.1; duration: 9000; easing.type: Easing.InOutQuad }
            NumberAnimation { from: root.width * 0.1; to: -glowOne.width * 0.15; duration: 9000; easing.type: Easing.InOutQuad }
        }
    }

    Rectangle {
        id: glowTwo
        width: parent.width * 0.34
        height: width
        radius: width / 2
        x: parent.width - width * 0.85
        y: parent.height - height * 0.75
        color: Qt.rgba(1, 1, 1, 0.10)
        opacity: 0.8
        SequentialAnimation on y {
            running: root.animated
            loops: Animation.Infinite
            NumberAnimation { from: parent.height - glowTwo.height * 0.75; to: parent.height - glowTwo.height * 0.92; duration: 7000; easing.type: Easing.InOutQuad }
            NumberAnimation { from: parent.height - glowTwo.height * 0.92; to: parent.height - glowTwo.height * 0.75; duration: 7000; easing.type: Easing.InOutQuad }
        }
    }
}

