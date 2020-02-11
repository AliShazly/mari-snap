import mari
import xml.etree.ElementTree as ET

# https://community.foundry.com/discuss/topic/143466/a-trick-to-set-your-node-position-via-python
def getNodePosition(graph, node):
    nodes = [node]

    # convert the node to a string in the clipboard
    nodestring = graph.nodesToString(nodes)

    # parse string as XML
    root = ET.fromstring(nodestring)

    # Node Position as List
    node_x_y = []

    # Find the first Node Position entry in the XML
    # Always the first because on Group Nodes multiple nodes are inside.
    for position in root.iter('position'):
        try:
            nodeposition = position.text
            lst = nodeposition.split(',')
            for nr in lst:
                node_x_y.append(float(nr))
            break
        except:
            pass
    return node_x_y


def offsetNodePosition(graph, node, offsetX, offsetY):
    nodestring = graph.nodesToString(nodes)
    node_x_y,node_pos_str = getNodePosition(graph,node)
    if len(node_x_y) != 0:
        # Set a new Node Position with offset
        newValueX = node_x_y[0] + offsetX
        newValueY =  node_x_y[1] + offsetY
        node_x_y[0] = newValueX
        node_x_y[1] = newValueY
        new_node_pos_str = str(node_x_y[0]) + ',' + str(node_x_y[1])

        # Replace nodeposition text in nodestring with new one
        toReplace = '<position Type="QPointF">' + node_pos_str + '</position>'
        replaceWith = '<position Type="QPointF">' + new_node_pos_str + '</position>'
        nodestring = nodestring.replace(toReplace,replaceWith)

    # Generate Node at new position
    newNode = graph.nodesFromString(nodestring)

    for n in nodes:
        graph.removeNode(n)

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
        
        

nodeGraph = mari.geo.current().nodeGraph()
selectedNodes = nodeGraph.selectedNodeList()

inputs, outputs = getNodeIO(n)
setNodeIO(n2, inputs, outputs)

