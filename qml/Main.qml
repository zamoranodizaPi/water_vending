import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Particles 2.15
import "components"

ApplicationWindow {
    id: root
    width: 1024
    height: 600
    visible: true
    color: "transparent"
    title: appBridge.branding.title

    property var paletteMap: appBridge.palette

    GradientBackground {
        anchors.fill: parent
        paletteMap: root.paletteMap
        animated: true
    }

    ParticleSystem { id: particleSystem }

    Emitter {
        system: particleSystem
        enabled: appBridge.particlesEnabled
        width: root.width
        height: 8
        emitRate: appBridge.particlesEnabled ? 24 : 0
        lifeSpan: 5000
        size: 10
        velocity: AngleDirection { angle: 90; angleVariation: 16; magnitude: 60; magnitudeVariation: 15 }
    }

    ImageParticle {
        system: particleSystem
        enabled: appBridge.particlesEnabled
        color: root.paletteMap.particleColor
        alpha: 0.38
        colorVariation: 0.08
    }

    SideDrawer {
        id: drawer
        width: 300
        height: parent.height
        open: appBridge.drawerOpen
        paletteMap: root.paletteMap
        brandTitle: appBridge.branding.title
        brandTagline: appBridge.branding.tagline
        systemName: appBridge.branding.systemName
        currentTheme: appBridge.themeName
        currentMode: appBridge.themeMode
        onCloseRequested: appBridge.toggleDrawer()
        onToggleModeRequested: appBridge.toggleMode()
        onCycleThemeRequested: appBridge.cycleTheme()
        onReturnHomeRequested: appBridge.goHome()
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 14

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 92
            radius: 28
            color: Qt.rgba(1, 1, 1, appBridge.themeMode === "light" ? 0.18 : 0.08)
            border.color: Qt.rgba(1, 1, 1, appBridge.themeMode === "light" ? 0.35 : 0.18)
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.margins: 18
                spacing: 16

                Rectangle {
                    Layout.preferredWidth: 58
                    Layout.preferredHeight: 58
                    radius: 20
                    color: root.paletteMap.panelAlt
                    border.width: 1
                    border.color: Qt.rgba(1, 1, 1, 0.35)
                    Text {
                        anchors.centerIn: parent
                        text: "💧"
                        font.pixelSize: 28
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 3
                    Text {
                        text: appBridge.branding.title
                        color: root.paletteMap.text
                        font.pixelSize: 28
                        font.bold: true
                    }
                    Text {
                        text: appBridge.branding.tagline
                        color: root.paletteMap.textSoft
                        font.pixelSize: 12
                    }
                }

                Rectangle {
                    Layout.preferredWidth: 190
                    Layout.preferredHeight: 56
                    radius: 18
                    color: root.paletteMap.panel
                    border.width: 1
                    border.color: Qt.rgba(1, 1, 1, 0.25)

                    Row {
                        anchors.centerIn: parent
                        spacing: 6
                        Text {
                            text: "Crédito"
                            color: root.paletteMap.textSoft
                            font.pixelSize: 14
                        }
                        Text {
                            text: "$" + Number(appBridge.credit).toFixed(2)
                            color: root.paletteMap.price
                            font.pixelSize: 24
                            font.bold: true
                        }
                    }
                }

                GlassButton {
                    text: "Menu"
                    width: 120
                    onClicked: appBridge.toggleDrawer()
                    paletteMap: root.paletteMap
                }
            }
        }

        StackLayout {
            id: contentStack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: appBridge.currentScreen === "home" ? 0 : appBridge.currentScreen === "payment" ? 1 : appBridge.currentScreen === "dispensing" ? 2 : 3

            Item {
                anchors.fill: parent
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 14

                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        text: "Seleccione un producto"
                        color: root.paletteMap.text
                        font.pixelSize: 18
                        font.bold: true
                    }

                    ListView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        orientation: ListView.Horizontal
                        spacing: 18
                        model: appBridge.productModel
                        interactive: false
                        delegate: ProductCard {
                            width: (contentStack.width - 36) / 3
                            height: contentStack.height - 42
                            paletteMap: root.paletteMap
                            productName: model.name
                            productVolume: model.volume
                            productPrice: model.price
                            productImage: model.image
                            accentColor: model.accent
                            selected: appBridge.selectedProductId === model.id
                            onChosen: appBridge.selectProduct(model.id)
                        }
                    }
                }
            }

            Rectangle {
                radius: 28
                color: Qt.rgba(1, 1, 1, appBridge.themeMode === "light" ? 0.16 : 0.08)
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 0.2)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 28
                    spacing: 18

                    Text {
                        text: "Confirme su selección"
                        color: root.paletteMap.text
                        font.pixelSize: 28
                        font.bold: true
                    }

                    Text {
                        text: appBridge.infoMessage
                        color: root.paletteMap.textSoft
                        font.pixelSize: 15
                    }

                    RowLayout {
                        spacing: 16
                        Repeater {
                            model: [1, 5, 10]
                            delegate: GlassButton {
                                text: "+$" + modelData
                                width: 132
                                paletteMap: root.paletteMap
                                onClicked: appBridge.addCredit(modelData)
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 18
                        GlassButton {
                            text: "Volver"
                            width: 150
                            paletteMap: root.paletteMap
                            secondary: true
                            onClicked: appBridge.goHome()
                        }
                        Item { Layout.fillWidth: true }
                        GlassButton {
                            text: "Continuar"
                            width: 200
                            paletteMap: root.paletteMap
                            emphasize: true
                            onClicked: appBridge.proceedFromPayment()
                        }
                    }
                }
            }

            Rectangle {
                radius: 28
                color: Qt.rgba(1, 1, 1, appBridge.themeMode === "light" ? 0.16 : 0.08)
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 0.2)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 30
                    spacing: 18

                    Text {
                        text: "Proceso de llenado"
                        color: root.paletteMap.text
                        font.pixelSize: 28
                        font.bold: true
                    }
                    Text {
                        text: appBridge.infoMessage
                        color: root.paletteMap.textSoft
                        font.pixelSize: 16
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 32
                        color: root.paletteMap.panel
                        opacity: 0.82
                        border.width: 1
                        border.color: Qt.rgba(1, 1, 1, 0.28)

                        Text {
                            anchors.centerIn: parent
                            text: Number(appBridge.progressValue).toFixed(0) + "%"
                            color: root.paletteMap.price
                            font.pixelSize: 58
                            font.bold: true
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 26
                        radius: 13
                        color: Qt.rgba(0, 0, 0, 0.12)

                        Rectangle {
                            width: parent.width * (appBridge.progressValue / 100)
                            height: parent.height
                            radius: 13
                            gradient: Gradient {
                                GradientStop { position: 0.0; color: root.paletteMap.buttonGradient[0] }
                                GradientStop { position: 0.5; color: root.paletteMap.buttonGradient[1] }
                                GradientStop { position: 1.0; color: root.paletteMap.buttonGradient[2] }
                            }
                            Behavior on width { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
                        }
                    }
                }
            }

            Rectangle {
                radius: 28
                color: Qt.rgba(1, 1, 1, appBridge.themeMode === "light" ? 0.16 : 0.08)
                border.width: 1
                border.color: Qt.rgba(1, 1, 1, 0.2)

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 30
                    spacing: 20

                    Text {
                        text: "Gracias por su compra"
                        color: root.paletteMap.text
                        font.pixelSize: 30
                        font.bold: true
                    }
                    Text {
                        text: appBridge.infoMessage
                        color: root.paletteMap.textSoft
                        font.pixelSize: 16
                    }
                    Item { Layout.fillHeight: true }
                    GlassButton {
                        Layout.alignment: Qt.AlignRight
                        text: "Volver al inicio"
                        width: 220
                        paletteMap: root.paletteMap
                        onClicked: appBridge.goHome()
                    }
                }
            }

            Behavior on currentIndex {
                NumberAnimation { duration: 260; easing.type: Easing.InOutCubic }
            }
        }
    }
}

