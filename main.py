import torch
import argparse

from A.modules.csv_utils import *

parser = argparse.ArgumentParser(description='Simple Script')

parser.add_argument('-rows', default='4', type=int)
parser.add_argument('-columns', default='5', type=int)
parser.add_argument('-batch', default='3', type=int)
parser.add_argument('-device', default='cuda', type=str)
args, args_other = parser.parse_known_args()


DEVICE = args.device
if not torch.cuda.is_available():
    DEVICE = 'cpu'

x = torch.randn((args.batch, args.rows, args.columns))
y = torch.randn((args.batch, args.rows, args.columns))

x = x.to(DEVICE)
y = y.to(DEVICE)

result = x + y

print(result.detach().cpu())


