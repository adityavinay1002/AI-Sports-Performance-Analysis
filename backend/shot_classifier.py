def classify_shot(angles, distances):
    """
    Classifies the cricket shot based on joint angles and distances.
    
    Args:
        angles (dict): Dictionary containing calculated angles.
            Expected keys: 'right_knee', 'left_knee', 'right_elbow', 'left_elbow', 
                           'right_hip', 'left_hip'
        distances (dict): Dictionary containing calculated distances.
            Expected keys: 'wrist_nose', 'right_left_leg'
            
    Returns:
        str: The name of the detected shot, or "Rest Shot" if no specific shot is detected.
    """
    
    # Unpack values for easier reading, matching the user's logic variable names
    right_knee_angle = angles.get('right_knee', 0)
    left_knee_angle = angles.get('left_knee', 0)
    right_elbow_angle = angles.get('right_elbow', 0)
    left_elbow_angle = angles.get('left_elbow', 0)
    right_hip_angle = angles.get('right_hip', 0)
    left_hip_angle = angles.get('left_hip', 0)
    
    wrist_nose_dist = distances.get('wrist_nose', 0)
    right_left_leg_dist = distances.get('right_left_leg', 0)
    
    shot = "Rest Shot"

    # Cover Drive
    if (170 > right_knee_angle > 90 and 
        160 > left_knee_angle > 80 and 
        145 > right_elbow_angle > 50 and 
        170 > left_elbow_angle > 55 and 
        180 > right_hip_angle > 120 and 
        165 > left_hip_angle > 100 and 
        13 > wrist_nose_dist > 5):
        shot = "Cover Drive"
            
    # Front Foot Defensive
    elif (180 > right_knee_angle > 100 and 
          165 > left_knee_angle > 100 and 
          (105 > right_elbow_angle > 50 or 180 > left_elbow_angle > 80) and 
          180 > right_hip_angle > 70 and 
          180 > left_hip_angle > 90 and 
          20 > wrist_nose_dist > 10 and 
          right_left_leg_dist > 10):
        shot = "Front Foot Defensive"
                
    # Back Foot Defensive
    elif (180 > right_knee_angle > 150 and 
          180 > left_knee_angle > 160 and 
          140 > right_elbow_angle and 
          140 > left_elbow_angle > 30 and 
          180 > right_hip_angle > 160 and 
          180 > left_hip_angle > 160 and 
          6 > wrist_nose_dist > 2 and 
          6 > right_left_leg_dist > 3):
        shot = "Back Foot Defensive"

    # Back Foot Punch
    elif (180 > right_knee_angle > 160 and 
          180 > left_knee_angle > 160 and 
          150 > right_elbow_angle > 70 and 
          180 > left_elbow_angle > 70 and 
          180 > right_hip_angle > 160 and 
          180 > left_hip_angle > 165 and 
          13 > wrist_nose_dist > 4 and 
          right_left_leg_dist > 3):
        shot = "Back Foot Punch"
            
    # Sweep Shot
    elif (110 > right_knee_angle > 70 and 
          180 > left_knee_angle > 100 and 
          180 > right_elbow_angle > 40 and 
          170 > left_elbow_angle > 90 and 
          175 > right_hip_angle > 120 and 
          175 > left_hip_angle > 90):
        shot = "Sweep Shot"
        
    # Pull Shot
    elif (180 > right_knee_angle > 150 and 
          180 > left_knee_angle > 150 and 
          180 > right_elbow_angle > 65 and 
          160 > left_elbow_angle > 20 and 
          180 > right_hip_angle > 160 and 
          180 > left_hip_angle > 160 and 
          13 > wrist_nose_dist > 2 and 
          12 > right_left_leg_dist > 1):
        shot = "Pull Shot"
        
    # Flick Shot
    elif (180 > right_knee_angle > 130 and 
          180 > left_knee_angle > 165 and 
          180 > right_elbow_angle > 110 and 
          160 > left_elbow_angle > 110 and 
          180 > right_hip_angle > 140 and 
          150 > left_hip_angle > 130):
        shot = "Flick Shot"
        
    return shot
