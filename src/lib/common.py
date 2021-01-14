import numpy as np
import os,joblib
import torch,random
import torch.nn as nn

def readImg(im_fn):
    im = cv2.imread(im_fn)
    if im is None :
        tmp = imageio.mimread(im_fn)
        if tmp is not None:
            imt = np.array(tmp)
            imt = imt[0]
            im = imt[:,:] #mask和gt是灰度图，取单通道
            #  _, im = cv2.threshold(im, 128, 255, cv2.THRESH_BINARY) #单通道不需要二值化处理，只有test中2nd_manual是四通道，暂时不考虑
    # print('loading image ：', im_fn)
    return im

def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count
        # print(self.val)

def make_lr_schedule(lr_epoch,lr_value):
    lr_schedule = np.zeros(lr_epoch[-1])
    for l in range(len(lr_epoch)):
        if l == 0:
            lr_schedule[0:lr_epoch[l]] = lr_value[l]
        else:
            lr_schedule[lr_epoch[l - 1]:lr_epoch[l]] = lr_value[l]
    return lr_schedule

def save_args(args,save_path):
    if not os.path.exists(save_path):
        os.makedirs('%s' % save_path)

    print('Config info -----')
    for arg in vars(args):
        print('%s: %s' % (arg, getattr(args, arg)))
    print('-----------------')

    with open('%s/args.txt' % save_path, 'w') as f:
        for arg in vars(args):
            print('%s: %s' % (arg, getattr(args, arg)), file=f)

    joblib.dump(args, '%s/args.pkl' % save_path)
    print('config infomation has been saved')


def setpu_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic=True
    random.seed(seed)

def dict_round(dic,num):
    for key,value in dic.items():
        dic[key] = round(value,num)
    return dic

# params initialization
def weight_init(m):
    if isinstance(m, nn.Conv2d):
        nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        if m.bias is not None:
            nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.constant_(m.weight, 1)
        nn.init.constant_(m.bias, 0)
    elif isinstance(m, nn.Linear):
        nn.init.normal_(m.weight, 0, 0.01)
        if m.bias is not None:
            nn.init.constant_(m.bias, 0)

def weight_init2(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_normal_(m.weight)
        nn.init.constant_(m.bias, 0)
    # 也可以判断是否为conv2d，使用相应的初始化方式 
    elif isinstance(m, nn.Conv2d):
        nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
     # 是否为批归一化层
    elif isinstance(m, nn.BatchNorm2d):
        nn.init.constant_(m.weight, 1)
        nn.init.constant_(m.bias, 0)
