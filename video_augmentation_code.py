import cv2
import os,PIL
import imgaug as ia
import imageio
from imgaug import augmenters as iaa
import shutil
import argparse
import random


def augment_and_save_frames(video_reader,rotation_angle,noise_value,output_folder_path,video_clip_name,i,fps):
    """
        Fetch each frame of video and augment and save as picture in a temporary folder
        Args:
            video_reader: Imageio reader object to read video frames 
            rotation_angle: int (Angle of rotation of image)
            noise_value: int (noise value between 0 to 100)
            temp_folder_path: string (temporary path to store video frames)
            output_folder_path: string (output folder path)
            video_clip_name: string (video name)
            i: no of clip augmented
            fps: int (Frames per second of original video)
    """

    seq = iaa.Sequential([
        iaa.Affine(rotate=rotation_angle),
        iaa.AdditiveGaussianNoise(scale=noise_value)
    ])
    
    temp_folder_path = f"{output_folder_path}//temp"
    print("Temporary folder path is ", temp_folder_path)
    if os.path.exists(temp_folder_path) and os.path.isdir(temp_folder_path):
        shutil.rmtree(temp_folder_path)
    os.makedirs(temp_folder_path) # Create a temp folder to save augmented frames in

    for count, im in enumerate(video_reader):
        image_aug = seq(image=im)
        count+=1
        imageio.imwrite(f"{temp_folder_path}//frame%d.jpg" % count,image_aug)

    temp = video_clip_name.replace(" ","")
    temp = temp.split(".")
    editted_name = temp[0]+"_"+str(i)+"."+temp[1]
    path_of_video_to_save = output_folder_path+"//"+editted_name
    save(fps,temp_folder_path,path_of_video_to_save)

def get_video_fps(video_path):
    """
        Get the FPS of input video clip, so that output video clip can also be saved with that FPS
        Args:
            video_path: string (Path of input video to be augmented)
        Return:
            fps: int (FPS)
    """
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.cv2.CAP_PROP_FPS)
    return fps

def save(fps,temp_folder_path,path_of_video_to_save):
    """
        Save the augmented clip in the chosen output folder
        Args:
            fps: int (FPS of video to be saved)
            temp_folder_path: str (Path of temporary folder where pics are saved, that would combine to form video
            path_of_video_to_save: str (Path of output augmented video to be saved)
    """
    print("Augmented video will be saved at ", path_of_video_to_save)
    os.system("ffmpeg -r {0} -i {1}//frame%d.jpg -vcodec mpeg4 -y {2}".format(fps,temp_folder_path,path_of_video_to_save))
    
if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--main-folder-path', type=str,default='',help='Path of folder that contains classes of clips to be augmented',required=True)
    parser.add_argument('--output-folder-path', type=str, default='',required=True,help='Path of folder that will contain augmented clips and a temporary folder for holding augmented images')
    parser.add_argument('--max-clips', type=int,required=True,help='Max number of clips to augment per input video sample. Make sure max_clips is less than difference between rotation angle')
    
    opt = parser.parse_args()
    print("opt \n",opt)
    main_folder_path=opt.main_folder_path
    output_folder_path=opt.output_folder_path
    max_augmented_clips_per_video = opt.max_clips
        
    print("Output folder", output_folder_path)
    print("Main folder", main_folder_path)
    print("Max augmented clips", max_augmented_clips_per_video)
    i=1
        
    if os.path.exists(output_folder_path) and os.path.isdir(output_folder_path):
        shutil.rmtree(output_folder_path)
    os.makedirs(output_folder_path)
    class_names = os.listdir(main_folder_path)
    print("Class names are ", class_names)
    
    # If the clips are stored according to their respective classes
    for clas in class_names:
        class_folder_path = f"{main_folder_path}//{clas}"
        video_clip_names = os.listdir(class_folder_path)
        output_class_path = output_folder_path+"//"+clas
        
        # Remove the output folder if it already exists to prevent over adding clips
        if os.path.exists(output_class_path) and os.path.isdir(output_class_path):
            shutil.rmtree(output_class_path)

        print(f"Videos found are {video_clip_names}")
        no_of_clips_available = len(video_clip_names)

        # Run for each clip that needs to be augmented
        for clip_no in range(no_of_clips_available):
            no_of_clips_to_augment_per_frame = max_augmented_clips_per_video
            # Rotate the clip based on angle range and increment the subsequent clips w.r.t. the angle increment
            print("No. of videos to be augmented per frame", no_of_clips_to_augment_per_frame)

            for i in range(no_of_clips_to_augment_per_frame):
                video_path = f"{class_folder_path}//{video_clip_names[clip_no]}"
                # Noise value to add to videos for augmentation
                noise_value = random.randint(0,60)
                # Rotation angle for video augmentation
                rotation_angle = random.randint(0,360)

                print("Rotation angle for augmented clip is ", rotation_angle)
                print("Noise value to add to augmented clip is ", noise_value)
                
                # Get fps for input video
                fps = get_video_fps(video_path)
                print(f"FPS of {video_clip_names[clip_no]} is {fps}")
                # Get video reader object
                reader = imageio.get_reader(video_path)
                augment_and_save_frames(reader,rotation_angle,noise_value,output_class_path,video_clip_names[clip_no],i,fps)
