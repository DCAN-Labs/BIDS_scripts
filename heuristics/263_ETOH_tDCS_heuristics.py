def create_key(template, outtype=('nii.gz','dicom'), annotation_classes=None): #), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return (template, outtype, annotation_classes)


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """
    
    # create heuristic keys to represent each file type
    
    
    t1 = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_acq-{acq}_run-{item:02d}_T1w')
    t2 = create_key('sub-{subject}/{session}/anat/sub-{subject}_{session}_acq-{acq}_run-{item:02d}_T2w')

    task = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-{acq}_run-{item:02d}_bold')
    sbref_task = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-{acq}_run-{item:02d}_sbref')

    rest = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_acq-{acq}_run-{item:02d}_bold')
    sbref_rest = create_key('sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_acq-{acq}_run-{item:02d}_sbref')

    dwi = create_key('sub-{subject}/{session}/dwi/sub-{subject}_{session}_acq-{acq}_run-{item:02d}_dwi')

    spinecho_map_bold = create_key('sub-{subject}/{session}/fmap/sub-{subject}_{session}_dir-{dir}_run-{item:02d}_epi')

    info = {t1: [], t2: [], task: [], rest: [], dwi: [], spinecho_map_bold: [], sbref_rest: [], sbref_task: []}
    
    
    # loop through acquired data
    for idx, s in enumerate(seqinfo):
        if idx + 1 < len(seqinfo) - 1:
            s_next = seqinfo[idx+1]
        if (s.dim3 == 208) and ('NORM' in s.image_type):
            if 'T1w' in s.dcm_dir_name:
                acq = 'T1MPR'
                info[t1].append({'item': s.series_id, 'acq': acq})
            else:
                acq = 'T2SPC'
                info[t2].append({'item': s.series_id, 'acq': acq})
        #find diffusion scans                
        elif (s.dim4 >= 79) and (('DWI_79dir_b1000_2000_REV_PA' in s.protocol_name) or ('DWI_79dir_b1000_2000_AP' in s.protocol_name)):
            info[dwi].append({'item': s.series_id, 'acq': 'AP'})    
        elif (s.dim4 >= 79) and ('DWI_79dir_b1000_2000_PA' in s.protocol_name):
            info[dwi].append({'item': s.series_id, 'acq': 'PA'})
        # find resting state scans
        elif (s.dim4 == 520):
            if ('REST_EC' in s.protocol_name):
                acq = 'eyesclosedPA'
            elif ('REST_EO_BEFORE' in s.protocol_name):
                acq = 'eyesopenbeforePA'
            elif ('REST_EO_AFTER' in s.protocol_name):
                acq = 'eyesopenafterPA'
            info[rest].append({'item': s.series_id, 'acq': acq})          
        elif (s.dim4 == 700) and (('REVERSAL_LEARNING' in s.protocol_name)):
            info[task].append({'item': s.series_id, 'acq': 'revlearnPA'})      
        # find single band reference images
        elif (s.dim4 == 1):
            if 'REST_E' in s.protocol_name and s_next.dim4 == 520:
                if ('REST_EC' in s.protocol_name):
                    acq = 'eyesclosedPA'
                elif ('REST_EO_BEFORE' in s.protocol_name):
                    acq = 'eyesopenbeforePA'
                elif ('REST_EO_AFTER' in s.protocol_name):
                    acq = 'eyesopenafterPA'
                info[sbref_rest].append({'item': s.series_id, 'acq': acq})
            elif 'REVERSAL_LEARNING' in s.protocol_name and s_next.dim4 == 700:
                info[sbref_task].append({'item': s.series_id, 'acq': 'revlearnPA'})
        # find fieldmaps
        elif (s.dim4 == 3) and ('SpinEchoFieldMap_PA' in s.protocol_name):
            info[spinecho_map_bold].append({'item': s.series_id, 'dir': 'PA'})
        elif (s.dim4 == 3) and ('SpinEchoFieldMap_REV_PA' in s.protocol_name):
            info[spinecho_map_bold].append({'item': s.series_id, 'dir': 'AP'})
    return info
