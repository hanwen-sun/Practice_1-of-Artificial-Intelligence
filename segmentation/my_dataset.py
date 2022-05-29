import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from torch.utils.data import Dataset as BaseDataset

def generate_path_list(root="Heart Data", mode="seg"):
    train_img_list, train_lab_list, valid_img_list, valid_lab_list = [], [], [], []
    assert os.path.exists(root), f"File {root} does not exist"

    if mode == "seg":
        mid_name = os.listdir(root)
        for f in mid_name:
            img_path = os.path.join(root, f, "png", "Image")
            for i in os.listdir(img_path):
                path = os.path.join(img_path, i)
                temp = os.listdir(path)
                for name in temp[0:-1]:
                    name = [os.path.join(path, name)]
                    train_img_list += name
                valid_img_list += [os.path.join(path, temp[-1])]

            lab_path = os.path.join(root, f, "png", "Label")
            for i in os.listdir(lab_path):
                path = os.path.join(lab_path, i)
                temp = os.listdir(path)
                for name in temp[0:-1]:
                    name = [os.path.join(path, name)]
                    train_lab_list += name
                valid_lab_list += [os.path.join(path, temp[-1])]

    return train_img_list, train_lab_list, valid_img_list, valid_lab_list


class Dataset(BaseDataset):
    def __init__(self, images_list, labels_list, augmentation=None, preprocessing=None):
        self.images_list = images_list
        self.labels_list = labels_list
        self.augmentation = augmentation
        self.preprocessing = preprocessing
        assert len(images_list) == len(labels_list), "Images and labels do not match"
        # values for 3 labels in gray picture
        self.class_values = [85, 170, 255]

    def __getitem__(self, i):
        # read data
        image = Image.open(self.images_list[i]).convert('RGB')
        image = np.array(image)
        label = Image.open(self.labels_list[i])
        label = np.array(label)

        # extract certain classes from mask
        masks = [(label == v) for v in self.class_values]
        mask = np.stack(masks, axis=-1).astype('float')

        # apply augmentations
        if self.augmentation:
            sample = self.augmentation(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']

        # apply preprocessing
        if self.preprocessing:
            sample = self.preprocessing(image=image, mask=mask)
            image, mask = sample['image'], sample['mask']

        return image, mask

    def __len__(self):
        return len(self.images_list)

if __name__=='__main__':

    x_train_dir = ["Heart Data/Image_DCM/png/Image/01/image1.png"]
    y_train_dir = ["Heart Data/Image_DCM/png/Label/01/label1.png"]

    dataset = Dataset(x_train_dir, y_train_dir)

    def visualize(**images):
        n = len(images)
        plt.figure(figsize=(16, 5))
        for i, (name, image) in enumerate(images.items()):
            plt.subplot(1, n, i + 1)
            plt.xticks([])
            plt.yticks([])
            plt.title(' '.join(name.split('_')).title())
            plt.imshow(image, cmap='gray')
        plt.show()

    image, mask = dataset[0]
    visualize(
        image=image,
        mask1=mask[:, :, 0],
        mask2=mask[:, :, 1],
        mask3=mask[:, :, 2],)