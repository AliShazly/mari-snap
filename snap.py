import mari
import xml.etree.ElementTree as ET
import time
from functools import wraps

HASH_SUFFIX = "nodeHash"

def timer(function):
    """Prints the time a function took to run"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = function(*args, **kwargs)
        end = time.time()
        elapsed = round(end - start, 2)
        print("{} took {} seconds.".format(function.__name__, elapsed))
        return result

    return wrapper

def getNodePosition(graph, node):
    nodestring = graph.nodesToString([node])

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

def precompNodeOffset(graph, node, nodeString, offsetX, offsetY):
    nodePos = getNodePosition(graph, node)
    nodePos_str = "{},{}".format(nodePos[0], nodePos[1])

    # Set a new Node Position with offset
    newX = nodePos[0] + offsetX
    newY = nodePos[1] + offsetY
    newNodePos_str = "{},{}".format(newX, newY)

    # Replace nodeposition text in nodeString with new one
    toReplace = "<position Type=\"QPointF\">{}</position>".format(nodePos_str)
    replaceWith = "<position Type=\"QPointF\">{}</position>".format(newNodePos_str)
    newNodeString = nodeString.replace(toReplace, replaceWith)

    return newNodeString

def getNodeIO(node):
    inputPorts = node.inputPortNames()
    inputs = {}
    for port in inputPorts:
        inputNode = node.inputNode(port)
        inputs[port] = getNodeHash(inputNode)

    outputNodes = node.outputNodes()
    outputs = {}
    for outputNode, outputPort in outputNodes:
        outputs[outputPort] = getNodeHash(outputNode)

    return inputs, outputs

def setNodeIO(node, graph, inputs, outputs):
    for inputPort, inputNodeHash in inputs.items():
        inputNode = getNodeByHash(graph, inputNodeHash)
        node.setInputNode(inputPort, inputNode)

    for outputPort, outputNodeHash in outputs.items():
        outputNode = getNodeByHash(graph, outputNodeHash)
        outputNode.setInputNode(outputPort, node)

def getNodeHash(node):
    try:
        return [tag for tag in node.tagList() if HASH_SUFFIX in tag][0]
    except IndexError:
        raise Exception("Node {} has no hash".format(node.name()))

def getNodeByHash(graph, nodeHash):
    for node in graph.nodeList():
        if any(HASH_SUFFIX in tag for tag in node.tagList()):
            return node

def setNodeHash(graph, node):
    if not any(HASH_SUFFIX in tag for tag in node.tagList()):
        nodeHash = "{}_{}".format(hash(graph.nodesToString([node])), HASH_SUFFIX)
        node.addTag(nodeHash)

@timer
def moveNodes(graph, nodes, offsetX, offsetY):
    nodeString = graph.nodesToString(nodes)
    nodesIO = []
    for node in nodes:
        setNodeHash(graph, node)
        nodeString = precompNodeOffset(graph, node, nodeString, offsetX, offsetY)
        nodesIO.append(getNodeIO(node))
        graph.removeNode(node)

    newNodes = graph.nodesFromString(nodeString)
    for node, nodeIO in zip(newNodes, nodesIO):
        inputs, outputs = nodeIO
        setNodeIO(node, graph, inputs, outputs)
        setNodeHash(graph, node)

nodeGraph = mari.geo.current().nodeGraph()
selectedNodes = nodeGraph.selectedNodeList()
moveNodes(nodeGraph, selectedNodes, 50, 50)

