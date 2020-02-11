import mari
import xml.etree.ElementTree as ET


def getNodePosition(graph, node):
    nodes = [node]

    # convert the node to a string in the clipboard
    nodestring = graph.nodesToString(nodes)

    # parse string as XML
    root = ET.fromstring(nodestring)

    # Node Position as List
    nodePos = []

    # Find the first Node Position entry in the XML
    # Always the first because on Group Nodes multiple nodes are inside.
    for position in root.iter('position'):
        try:
            lst = position.text.split(',')
            for i in lst:
                nodePos.append(float(i))
            break
        except:
            pass
    return nodePos


def offsetNodePosition(graph, node, offsetX, offsetY):

    nodestring = graph.nodesToString([node])
    nodePos = getNodePosition(graph, node)
    stringNodePos = "{},{}".format(nodePos[0], nodePos[1])

    # Set a new Node Position with offset
    newX = nodePos[0] + offsetX
    newY = nodePos[1] + offsetY
    newStringNodePos = "{},{}".format(newX, newY)

    # Replace nodeposition text in nodestring with new one
    toReplace = "<position Type=\"QPointF\">{}</position>".format(stringNodePos)
    replaceWith = "<position Type=\"QPointF\">{}</position>".format(newStringNodePos)
    nodestring = nodestring.replace(toReplace,replaceWith)

    # Generate Node at new position and remove old one
    newNode = graph.nodesFromString(nodestring)[0]
    graph.removeNode(node)

    return newNode


def getNodeIO(node):
    inputPorts = node.inputPortNames()
    inputs = {}
    for port in inputPorts:
        inputNode = node.inputNode(port)
        inputs[port] = inputNode
    outputNodes = node.outputNodes()
    outputs = {}
    for outputNode, outputPort in outputNodes:
        outputs[outputPort] = outputNode

    return inputs, outputs


def setNodeIO(node, inputs, outputs):
    for (inputPort, inputNode), (outputPort, outputNode) in zip(inputs.items(), outputs.items()):
        node.setInputNode(inputPort, inputNode)
        outputNode.setInputNode(outputPort, node)


def moveNode(graph, node, offsetX, offsetY):
    inputs, outputs = getNodeIO(node)
    newNode = offsetNodePosition(graph, node, offsetX, offsetY)
    setNodeIO(newNode, inputs, outputs)
    return newNode

nodeGraph = mari.geo.current().nodeGraph()
selectedNodes = nodeGraph.selectedNodeList()
moveNode(nodeGraph, selectedNodes[0], 50, 50)
