#encoding utf-8

import re
import sys

import os
from xml.dom import minidom, Node


reload(sys)
sys.setdefaultencoding('utf8')

#================CONFIG==========================
protoPath = "C:/workspaces/datas/protocol/"
appPath = "C:/workspaces/wp_laya/app_ts/"


#================FILEPATH========================
outPath = appPath + "src/app/net/auto/"
_dataUrl = protoPath + "data/";
_msgPath = protoPath + "msg/";


classTemplate = open("template/ts/class.ftmp").read()
requestTemplate = open("template/ts/request.ftmp").read()
responseTemplate = open("template/ts/response.ftmp").read()
dataTemplate = open("template/ts/data.ftmp").read()

def _regTemplate(template , data):
    def _reg(m):
        key = m.group()
        param = key[2:-1]
        return data[param]
    return re.sub(r'{@\w+}',_reg , template)

def _t2cType(t , element  = ""):
    inType = t.lower()
    if inType == "u8" or inType == "i8" or inType == "u16" or inType == "i16" or inType == "u32" or inType == "i32" or inType == "f32" or inType == "f64"\
            or inType == "int" or inType == "short" or inType == "number":
        return "number"
    if inType == "u64":
        return "Uint64"
    if inType == "string":
        return "string"
    if inType == "array" or inType == "[]":
        return _t2cType(element) +"[]"
    return t if t != "" else "Object"

def _writeParam( name , pType , sp="\t\t\t" ,element = ""):
    if pType == "i8":
        return sp + "ByteUtil.writeByte( byte, " + name + ");\n"
    elif pType == "i16" or pType == "short":
        return sp + "ByteUtil.writeInt16( byte, " + name + ");\n"
    elif pType == "i32" or pType == "int":
        return sp + "ByteUtil.writeInt32(byte, " + name + ");\n"
    elif pType == "u8":
        return sp + "ByteUtil.writeUint8(byte, " + name + ");\n"
    elif pType == "u16":
        return sp + "ByteUtil.writeUint16(byte, " + name + ");\n"
    elif pType == "u32":
        return sp + "ByteUtil.writeUint32(byte, " + name + ");\n"
    elif pType == "u64":
        return sp + "ByteUtil.writeUint64(byte, " + name + ");\n"
    elif pType == "f32":
        return sp + "ByteUtil.writeFloat32(byte, " + name + ");\n"
    elif pType == "f64" or pType.lower() == "number":
        return sp + "ByteUtil.writeFloat64(byte, " + name + ");\n"
    elif pType == "string":
        return sp + "ByteUtil.writeString(byte, " + name + ");\n"
    elif pType == "array" or pType == "[]":
        if element == "i8":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeByte);\n"
        elif pType == "i16" or element == "short":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeInt16);\n"
        elif element == "i32" or element == "int":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeInt32);\n"
        elif element == "u8":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeUint8);\n"
        elif element == "u16":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeUint16);\n"
        elif element == "u32":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeUint32);\n"
        elif element == "u64":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeUint64);\n"
        elif element == "f32":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeFloat32);\n"
        elif element == "f64" or pType.lower() == "number":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeUint64);\n"
        elif element.lower() == "string":
            return sp + "ByteUtil.writeArray(byte, " + name + " , ByteUtil.writeString);\n"
        else:
            return sp + "ByteUtil.writeArray(byte , " + name + " , " + element + ".writeByte);\n"
    else:
        return  sp + pType + ".writeByte(byte , " + name +");\n"

def _readParam( name , pType , sp="\t\t\t" ,element = ""):
    lType = pType.lower();
    if lType == "i8":
        return sp + name + " = ByteUtil.readInt8(byte);\n"
    elif lType == "i16" or lType == "short":
        return sp + name + " = ByteUtil.readInt16(byte);\n"
    elif lType == "i32" or lType == "int":
        return sp + name + " = ByteUtil.readInt32(byte);\n"
    elif lType == "u8":
        return sp + name + " = ByteUtil.readUint8(byte);\n"
    elif lType == "u16":
        return sp + name + " = ByteUtil.readUint16(byte);\n"
    elif lType == "u32":
        return sp + name + " = ByteUtil.readUint32(byte);\n"
    elif lType == "u64":
        return sp + name + " = ByteUtil.readUint64(byte);\n"
    elif lType == "f32":
        return sp + name + " = ByteUtil.readFloat32(byte);\n"
    elif lType == "f64":
        return sp + name + " = ByteUtil.readFloat64(byte);\n"
    elif lType == "string":
        return sp + name + " = ByteUtil.readString(byte);\n"
    elif lType == "array" or lType == "[]":
        lEle = element.lower()
        if lEle == "i8":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readInt8);\n"
        elif lEle == "i16" or lEle == "short":
            return sp + name + "ByteUtil.readArray(byte , ByteUtil.readInt16);\n"
        elif lEle == "i32" or lEle == "int":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readInt32);\n"
        elif lEle == "u8":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readUint8);\n"
        elif lEle == "u16":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readUint16);\n"
        elif lEle == "u32":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readUint32);\n"
        elif lEle == "u64":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readUint64);\n"
        elif lEle == "f32":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readFloat32);\n"
        elif lEle == "f64" or lEle == "number":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readFloat64);\n"
        elif lEle == "string":
            return sp + name + " = ByteUtil.readArray(byte , ByteUtil.readString);\n"
        else:
            return sp + name + " = ByteUtil.readArray(byte , " + element + ".readByte);\n"
    else:
        return sp + name + " = " + pType + ".readByte(byte);\n"


# protoList = []
_dataBuffer = ""
_responseDataBuffer = ""

def _scanDataNode(children,target):
    for child in children:
        if child.nodeType == Node.ELEMENT_NODE:
            if child.tagName == "prop":
                name = child.getAttribute("name")
                cType = child.getAttribute("type")
                element = child.getAttribute("element")
                desc = child.getAttribute("desc")
                target["param"] += "\tpublic " + name + " : " + _t2cType(cType,element) + ";\t//" + desc + "\n";
                target["read"] += _readParam("data." + name , cType , '\t\t',element )
                target["write"] += _writeParam("data." + name , cType  , '\t\t',element)
    target["read"] = target["read"][:-1]
    target["write"] = target["write"][:-1]

for root , dirs , files in os.walk(_dataUrl):
    for name in files:
        if name.find(".xml") != len(name) - 4:
            continue
        # protoList.append(os.path.join(root,name))
        f = open(os.path.join(root,name))
        try:
            xmlDoc = minidom.parse(f)
        except "Exception":
            pass
        for node in xmlDoc.childNodes:
            for n in node.childNodes:
                if n.nodeType == Node.ELEMENT_NODE:
                    if n.nodeName == "item":
                        name = n.getAttribute("name")
                        desc = n.getAttribute("desc")
                        parent = n.getAttribute("parent")
                        obj = {
                            "name":name,
                            "desc":desc,
                            "extend": " extends " + parent if parent else "",
                            "write":"\t\t" + parent + ".writeByte(byte,data);\n" if parent else "",
                            "read":"\t\t" + parent + ".readByte(byte,data);\n" if parent else "",
                            "param":""

                        }
                    _scanDataNode(n.childNodes,obj)
                    _dataBuffer += _regTemplate(dataTemplate,obj)


#Write
# ProtocolData
# os.mkdir(outPath)
f = open(outPath + "ProtocolData.ts","w")
f.write("/**==============ProtocolData======================*/\n")
f.write(_dataBuffer)
f.write("\n/**==============Response======================*/\n")
f.write(_responseDataBuffer)
f.close()












