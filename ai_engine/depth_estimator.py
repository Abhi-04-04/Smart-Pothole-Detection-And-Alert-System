# import torch
# import cv2

# class DepthEstimator:

#     def __init__(self):

#         self.model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
#         self.model.eval()

#     def estimate(self, image_path):

#         img = cv2.imread(image_path)
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#         tensor = torch.from_numpy(img).float().permute(2,0,1).unsqueeze(0)

#         with torch.no_grad():
#             depth = self.model(tensor)

#         return float(depth.mean())
##################################################################

import torch
import cv2


class DepthEstimator:

    def __init__(self):

        self.model = torch.hub.load(
            "intel-isl/MiDaS",
            "MiDaS_small"
        )

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.model.to(self.device)
        self.model.eval()

        self.transforms = torch.hub.load(
            "intel-isl/MiDaS",
            "transforms"
        ).small_transform


    def estimate_depth(self, frame):

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        input_batch = self.transforms(img).to(self.device)

        with torch.no_grad():

            prediction = self.model(input_batch)

            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode="bicubic",
                align_corners=False
            ).squeeze()

        depth_map = prediction.cpu().numpy()

        return depth_map