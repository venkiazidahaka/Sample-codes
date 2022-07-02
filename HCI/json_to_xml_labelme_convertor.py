import json
import xml.etree.cElementTree as ET
import glob
from tqdm import tqdm


def read_json(json_file_path):
    with open(json_file_path) as f:
        json_file = json.load(f)

    return json_file


def extract_json_file_data(json_file):
    shapes = json_file["shapes"]
    # print(shapes)
    object_list = []
    for shape in shapes:
        name = shape["label"]
        points = shape["points"]
        object_type = shape["shape_type"]
        single_object = [object_type, name, points]
        object_list.append(single_object)

    return object_list


def create_xml_file(image_name, object_list):
    root = ET.Element("annotation")

    filename = ET.SubElement(root, "filename")
    filename.text = image_name

    ET.SubElement(root, "folder")

    source = ET.SubElement(root, "source")
    ET.SubElement(source, "sourceImage")
    sourceAnnotation = ET.SubElement(source, "sourceAnnotation")
    sourceAnnotation.text = "Datumaro"

    imagesize = ET.SubElement(root, "imagesize")
    nrows = ET.SubElement(imagesize, "nrows")
    ncols = ET.SubElement(imagesize, "ncols")
    nrows.text = "720"
    ncols.text = "1280"

    for identity, single_object in enumerate(object_list):
        objects = ET.SubElement(root, "object")

        name = ET.SubElement(objects, "name")
        name.text = single_object[1]

        deleted = ET.SubElement(objects, "deleted")
        deleted.text = "0"

        verified = ET.SubElement(objects, "verified")
        verified.text = "0"

        occluded = ET.SubElement(objects, "occluded")
        occluded.text = "no"

        ET.SubElement(objects, "date")

        annotation_id = ET.SubElement(objects, "id")
        annotation_id.text = str(identity)

        parts = ET.SubElement(objects, "parts")
        ET.SubElement(parts, "hasparts")
        ET.SubElement(parts, "ispartof")

        annotation_type = ET.SubElement(objects, single_object[0])
        for point in single_object[2]:
            pt = ET.SubElement(annotation_type, "pt")
            x = ET.SubElement(pt, "x")
            y = ET.SubElement(pt, "y")
            x.text = str(int(point[0]))
            y.text = str(int(point[1]))

        ET.SubElement(objects, "username")

        attributes = ET.SubElement(objects, "attributes")
        attributes.text = "z_order=0"

    tree = ET.ElementTree(root)

    return tree


def write_xml(tree, save_path, save_name):
    savepath = save_path + "/" + save_name + ".xml"
    tree.write(savepath)


def get_image_name(file_path):
    seperator = "\\"
    file_path_split = file_path.split(seperator)
    file_name = file_path_split[-1]
    file_name_split = file_name.split(".")
    image_name = file_name_split[0]

    return image_name


def main(source_directory, save_directory):
    file_path_list = glob.glob(source_directory + "/*.json")

    for file_path in tqdm(file_path_list, desc="converting to xml file"):
        name = get_image_name(file_path)
        json_file = read_json(file_path)
        object_list = extract_json_file_data(json_file)
        image_name = name + ".jpg"
        tree = create_xml_file(
            image_name, object_list)
        write_xml(tree, save_directory,
                  name)


if __name__ == "__main__":
    file_path = "C:/Users/segroup/Documents/code/18D0004/Flat_cable_test_1/datumaro"
    # json_file = read_json(file_path)
    # # print(json_file)
    # object_list = extract_json_file_data(json_file)
    # # print(object_list)
    # tree = create_xml_file("WIN_20210204_18_37_17_Pro_00010.jpg", object_list)
    # # print(tree)
    # write_xml(tree, "C:/Users/segroup/Documents/code/18D0004/Flat_cable_test_1/datumaro",
    #           "WIN_20210204_18_37_17_Pro_00010")
    # # tree.write(
    # #     "C:/Users/segroup/Documents/code/18D0004/Flat_cable_test_1/datumaro/WIN_20210204_18_37_17_Pro_00010.xml")
    main(file_path, file_path)
