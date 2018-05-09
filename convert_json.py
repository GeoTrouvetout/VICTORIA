#!/usr/bin/python3

import os
import sys
import argparse 

import numpy as np

import time
import json

import pandas as pd

from pymediainfo import MediaInfo



def main(args):
    
    with open(args.json) as json_data:
        d = json.load(json_data)
        videoname = d['video_name']
        filename = os.path.splitext(os.path.basename(args.json))[0]
        print(filename)
        cfile = filename.split("Cut")[0]
        cameraid = cfile[-2:]
        if not cameraid[0]=='C':
            cameraid = "C" + str(cameraid)
            
        
        directory = args.resultdir + "/" + cfile + "/"
        
        df = pd.read_csv("/media/grj/Data/Work/IRIT/DATA/corpus-irit/TOCADA_cam.csv", delimiter=';')
        print(cameraid)
        camera_info = np.array( df.loc[ df['ID'] == cameraid ] )
        print(camera_info)
        camera_info = camera_info[0]
        numF = cfile[1]
        media_info = MediaInfo.parse("/media/grj/Data/Work/IRIT/DATA/corpus-irit/F_CutH264/F"+str(numF)+"/"+filename+".mp4")
        media_info = media_info.to_data()
#         print(media_info)
        for tracks in media_info['tracks']:
#             print(tracks)
            if tracks['track_type'] == 'General':
                general_info = tracks
            if tracks['track_type'] == 'Video':
                video_info = tracks
            if tracks['track_type'] == 'Audio':
                audio_info = tracks
#         print(video_info)        
        
        if not os.path.exists(directory):
            os.makedirs(directory)
#         
        for i in range(len(d['frame'])):
            frame = {}
            frame['video_file_name'] = general_info['file_name']
            frame['video_file_extension'] = general_info['file_extension']
            frame['video_format'] = general_info['format']
            frame['video_file_size'] = general_info['file_size']
            frame['video_other_file_size'] = general_info['other_file_size']
            frame['video_duration_ms'] = general_info['duration']
            frame['video_other_duration'] = video_info['other_duration']
            frame['video_frame_rate'] = video_info['frame_rate']
            
            
  
            frame['video_overall_bit_rate'] = general_info['overall_bit_rate']
            frame['video_other_overall_bit_rate'] = general_info['other_overall_bit_rate']
            frame['video_frame_count'] = general_info['frame_count']
            frame['video_color_space'] = video_info['color_space']
            frame['video_chroma_subsampling'] = video_info['chroma_subsampling']
            frame['video_bit_depth'] = video_info['bit_depth']
            frame['video_scan_type'] = video_info['scan_type']
            frame['video_interlacement'] = video_info['interlacement']
            frame['video_bits_pixel_frame'] = video_info['bits__pixel_frame']
            
            frame['audio_format'] = audio_info['format']
            frame['audio_bit_rate'] = audio_info['bit_rate']
            frame['audio_other_bit_rate'] = audio_info['other_bit_rate']
            frame['audio_channel_s'] = audio_info['channel_s']
            frame['audio_channellayout'] = audio_info['channellayout']
            frame['audio_samples_per_frame'] = audio_info['samples_per_frame']
            frame['audio_sampling_rate'] = audio_info['sampling_rate']
            frame['audio_other_sampling_rate'] = audio_info['other_sampling_rate']
            frame['audio_frame_rate'] = audio_info['sampling_rate']
            frame['audio_compression_mode'] = audio_info['compression_mode']
            
            frame['camera_id'] = cameraid
            frame['camera_place'] = camera_info[1]
            frame['camera_quality'] = camera_info[2]
            frame['camera_team'] = camera_info[3]
            frame['camera_type'] = camera_info[4]
            frame['camera_details'] = camera_info[5]
            frame['camera_owner'] = camera_info[6]
            frame['camera_geolocation']={"type" : "Point",
                                         "coordinates" : [camera_info[8], camera_info[7]]}
            frame['camera_fov_polygon']={
                "type" : "Polygon",
                "coordinates":[
                    [
                        [camera_info[8],camera_info[9]],
                        [camera_info[10],camera_info[9]],
                        [camera_info[12],camera_info[11]], 
                        [camera_info[8],camera_info[9]]
                    ]
                ]
            } 

            frame['frame_number'] = d['frame'][i]['frame_number']
            frame['frame_timestamp'] = d['frame'][i]['frame_timestamp']
            frame['frame_width'] = video_info['width']
            frame['frame_height'] = video_info['height']
            frame['frame_aspect_ratio'] = video_info['display_aspect_ratio']
            frame['frame_other_aspect_ratio'] = video_info['other_display_aspect_ratio']
            frame['frame_stats'] = d['frame'][i]['frame_stats']
            objects = d['frame'][i]['object']
            frame_objects = []
            for o in objects:
                polygon = [
                    [ o['bbox']['bottomright']['x'], o['bbox']['bottomright']['y'] ],
                    [ o['bbox']['bottomright']['x'], o['bbox']['topleft']['y'] ],
                    [ o['bbox']['topleft']['x'], o['bbox']['topleft']['y'] ],
                    [ o['bbox']['topleft']['x'], o['bbox']['bottomright']['y'] ],
                    [ o['bbox']['bottomright']['x'], o['bbox']['bottomright']['y'] ]
                ]
                obj = {
                    'category' : o['category'],
                    'details' : o['details'],
                    'confidence' : o['confidence'],
                    'bounding_box' : {
                        "type" : "polygon",
                        "coordinates": polygon 
                    }
                }

                frame_objects.append(obj)

            frame['frame_objects'] = frame_objects
            jsonfilename = directory + filename +"_f" + str(i) + ".json" 
                
            with open(jsonfilename, 'w', encoding="utf-8") as outfile:
                 json.dump(frame, outfile)
             
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract a sequence in a video file between [startframe] and [endframe]. ")
    parser.add_argument("-i", "--json", 
                        dest="json",
                        type=str,
                        help="input json",)
    parser.add_argument("-r", "--result-directories",
                        dest="resultdir",
                        type=str, 
                        default="./",
                        help="result directorie to save",)
    args = parser.parse_args()
    main(args)
    

