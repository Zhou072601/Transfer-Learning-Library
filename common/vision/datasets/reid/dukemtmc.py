from .basedataset import BaseImageDataset
import os.path as osp
import glob
import re
from common.vision.datasets._util import download


class DukeMTMC(BaseImageDataset):
    """DukeMTMC-reID dataset from `Performance Measures and a Data Set for Multi-Target, Multi-Camera Tracking
    (ECCV 2016) <https://arxiv.org/pdf/1609.01775v2.pdf>`_.

    Dataset statistics:
        - identities: 1404 (train + query)
        - images:16522 (train) + 2228 (query) + 17661 (gallery)
        - cameras: 8

    Args:
        root (str): Root directory of dataset
        verbose (bool, optional): If true, print dataset statistics after loading the dataset. Default: True
    """
    dataset_dir = '.'
    archive_name = 'DukeMTMC-reID.tgz'
    dataset_url = 'https://cloud.tsinghua.edu.cn/f/89f1edaf0f83434f8070/?dl=1'

    def __init__(self, root, verbose=True):
        super(DukeMTMC, self).__init__()
        download(root, self.dataset_dir, self.archive_name, self.dataset_url)
        self.dataset_dir = osp.join(root, self.dataset_dir)
        self.dataset_url = 'http://vision.cs.duke.edu/DukeMTMC/data/misc/DukeMTMC-reID.zip'
        self.train_dir = osp.join(self.dataset_dir, 'DukeMTMC-reID/bounding_box_train')
        self.query_dir = osp.join(self.dataset_dir, 'DukeMTMC-reID/query')
        self.gallery_dir = osp.join(self.dataset_dir, 'DukeMTMC-reID/bounding_box_test')

        required_files = [self.dataset_dir, self.train_dir, self.query_dir, self.gallery_dir]
        self.check_before_run(required_files)

        train = self.process_dir(self.train_dir, relabel=True)
        query = self.process_dir(self.query_dir, relabel=False)
        gallery = self.process_dir(self.gallery_dir, relabel=False)

        if verbose:
            print("=> DukeMTMC-reID loaded")
            self.print_dataset_statistics(train, query, gallery)

        self.train = train
        self.query = query
        self.gallery = gallery

        self.num_train_pids, self.num_train_imgs, self.num_train_cams = self.get_imagedata_info(self.train)
        self.num_query_pids, self.num_query_imgs, self.num_query_cams = self.get_imagedata_info(self.query)
        self.num_gallery_pids, self.num_gallery_imgs, self.num_gallery_cams = self.get_imagedata_info(self.gallery)

    def process_dir(self, dir_path, relabel=False):
        img_paths = glob.glob(osp.join(dir_path, '*.jpg'))
        pattern = re.compile(r'([-\d]+)_c(\d)')

        pid_container = set()
        for img_path in img_paths:
            pid, _ = map(int, pattern.search(img_path).groups())
            pid_container.add(pid)
        pid2label = {pid: label for label, pid in enumerate(pid_container)}

        dataset = []
        for img_path in img_paths:
            pid, camid = map(int, pattern.search(img_path).groups())
            assert 1 <= camid <= 8
            camid -= 1  # index starts from 0
            if relabel: pid = pid2label[pid]
            dataset.append((img_path, pid, camid))

        return dataset
