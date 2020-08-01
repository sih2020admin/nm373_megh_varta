from PIL import Image
import numpy as np
import os


def Preprocessed_additional_data(path,normalization_type,start_img_path, end_img_path,inp_seq_len=3,pred_frame=1,normalized_output='no',Validation_split=None):
    #path = "/home/prasad/SIH/oct/tir/" 
    files = os.listdir( path )
    files=sorted(files)
    files = [elem for elem in files if int(elem[18:20]) % 30 == 0] 
    files=np.array(files)

    
    end_loc=np.where(files==end_img_path)   #'3DIMG_07NOV2019_0000_L1C_SGP_IMG_TIR1.tif'
    start_loc=np.where(files==start_img_path)
    #print(end_loc,start_loc)
    end_index=end_loc[0][0]
    start_index=start_loc[0][0]
    
    files=files[start_index:end_index+1]
    
    date=[]
    month=[]
    time=[]
    for i in range(len(files)):
        date.append(int(files[i][6:8]))
        month.append(files[i][8:9])
        h=float(files[i][16:18])
        m=float(files[i][18:20])
        Time= h+ (m/60)
        time.append(Time)
    
    images_path=[]
    for i in range(len(files)):
        img_path= path+ files[i]
        images_path.append(img_path)
        
    print('loading images')
    X=[]
    i=0
    for image in images_path:
        if i%50==0:
            if i>0:
                print(i,"images out of", len(images_path), "are loaded")
        img = np.array( Image.open(image), dtype= np.double )[480:1464,1200:2274]
        
        X.append(img)
        i=i+1
    X=np.array(X)
    
    #print(mean,std_dev)
    window_size=inp_seq_len  #10
    
    if(Validation_split!=None):
        num_inp = len(X)-window_size
        #print(num_inp)
        ind = int(num_inp*Validation_split)
        if ind!=0:
            mean, std_dev = (X[:ind]).mean(),(X[:ind]).std()
            print('dataset is too small for validation set')
        else:
            mean, std_dev = X.mean(),X.std()
            
    else:
        mean, std_dev = X.mean(),X.std()

    Max,Min= np.max(X),np.min(X)
    
    
    print('normalizing images')
   
    i=0
    normalised_X=[]
    for img in X:
        if normalization_type=='scaling':
            norm= ((img-Min)/(Max-Min))
        if normalization_type=='zscore':
            norm = ((img - mean)/std_dev)
        normalised_X.append(norm)
        if i%50==0:
            if i>0:
                print(i,"images out of", len(X), "are normalized")
        i=i+1
     
            
    
    print('making images sequences with length:', window_size)
    
   
    if normalized_output=='yes':
        output='norm'
    else:
        output='not_normalized'
    
    verify=[]
    tir_x=[]
    tir_y=[]
    #print('lenX',len(X))
    
    for i in range(len(X)):
        if (i+window_size+pred_frame-1)>(len(X)-1):
            break

        flag=False

        chk=0
        for j in range(i,i+window_size+pred_frame-1):
            if ((time[j+1]==time[j]+0.5) and (date[j]==date[j+1])) or ((time[j]==23.5 and time[j+1]==0.0) and(date[j+1]==date[j]+1)):
                chk= chk+1
                #print(i,j,chk)

        if chk==window_size+pred_frame-1:
            flag=True

        if flag:
            #x=normalised_X[i:i+window_size]
            x=X[i:i+window_size]

            path=images_path[i:i+window_size+pred_frame]
            
            if output=='norm':
                y=normalised_X[i+window_size:i+window_size+pred_frame]
            else:
                y=X[i+window_size:i+window_size+pred_frame]
            
            y=X[i+window_size:i+window_size+pred_frame]
            #print(i)
            tir_x.append(x)
            tir_y.append(y)
            verify.append(path)
        if i%50==0:
            if i>0:
                print(i,"images out of", len(X), "are processed")
            
    tir_x=np.array(tir_x)
    tir_y=np.array(tir_y)
    #print(tir_x.shape)

    tir_x=np.reshape(tir_x, (tir_x.shape[0],tir_x.shape[1],tir_x.shape[2],tir_x.shape[3],1))  
    if pred_frame>1:
        tir_y=np.reshape(tir_y, (tir_y.shape[0],y.shape[1],tir_y.shape[2],tir_y.shape[3],1))  
    else:
        tir_y=np.reshape(tir_y, (tir_y.shape[0],tir_y.shape[2],tir_y.shape[3],1)) 


    if(Validation_split!=None)and(ind!=0):
        X_train=tir_x[:ind]
        y_train=tir_y[:ind]
        X_val=tir_x[ind:]
        y_val=tir_y[ind:]
    if(Validation_split!=None)and(ind==0):
        print('dataset too small for validation set')
        X_train=tir_x
        y_train=tir_y
        X_val=None
        y_val=None
    if(Validation_split==None):
        X_train=tir_x
        y_train=tir_y
        X_val=None
        y_val=None

    if normalization_type=='scaling':
        return (X_train,y_train,X_val,y_val,Max,Min,verify)        
    if normalization_type=='zscore':
        return (X_train,y_train,X_val,y_val,mean,std_dev,verify)       
    
    #return (tir_x,tir_y,X_val,y_val,mean,std_dev,verify)
    
def read1day_data(dir_path,inp_seq_len=3,pred_frame=1,normalized_output='no'):
    files_list=os.listdir(dir_path)
    files_list= sorted(files_list)

    files_reg_list = [ elem for elem in files_list if int(elem[18:20]) % 30 == 0] 
    #file_path ="./../pytorch-unet/INSAT3D_TIR1_India/" 
    
    files=[]
    files_name=[]
    for i in range(len(files_reg_list)):
        img = np.array(Image.open(os.path.join(dir_path,files_reg_list[i]) ))
        files.append(img)
        files_name.append(files_reg_list[i])
        
    files=np.array(files)
    
    raw_files_1  = files[:34]

    files_name_1 = files_name[:34]

    
    raw_files_2  = files[34:]

    files_name_2 = files_name[34:]
    
    
    window_size= inp_seq_len #10
    
    verify=[]
    tir_x=[]
    tir_y=[]
    for i in range(len(raw_files_1)):
        if (i+window_size+pred_frame-1)>(len(raw_files_1)-1):
            break
        x=raw_files_1[i:i+window_size]
        path=files_name_1[i:i+window_size+pred_frame]
        y=raw_files_1[i+window_size:i+window_size+pred_frame]
        
        verify.append(path)
        tir_x.append(x)
        tir_y.append(y)

    #tir_x,tir_y
    for i in range(len(raw_files_2)):
        if (i+window_size+pred_frame-1)>(len(raw_files_2)-1):
            break
        x=raw_files_2[i:i+window_size]
        path=files_name_2[i:i+window_size+pred_frame]
        y=raw_files_2[i+window_size:i+window_size+pred_frame]
        
        verify.append(path)    
        tir_x.append(x)
        tir_y.append(y)

    tir_x=np.array(tir_x)
    tir_y=np.array(tir_y)

    tir_x=np.reshape(tir_x, (tir_x.shape[0],tir_x.shape[1],tir_x.shape[2],tir_x.shape[3],1))  
    if pred_frame>1:
        tir_y=np.reshape(tir_y, (tir_y.shape[0],y.shape[1],tir_y.shape[2],tir_y.shape[3],1))  
    else:
        tir_y=np.reshape(tir_y, (tir_y.shape[0],tir_y.shape[2],tir_y.shape[3],1)) 
        

    X= tir_x
    y=tir_y
    
    return(X,y,verify)

def Preprocessed_1day_data(dir_path,normalization_type,inp_seq_len=3,pred_frame=1,normalized_output='no'):
    #dir_path ="./../pytorch-unet/INSAT3D_TIR1_India/" 
    files_list=os.listdir(dir_path)
    files_list= sorted(files_list)

    files_reg_list = [ elem for elem in files_list if int(elem[18:20]) % 30 == 0] 
    #file_path ="./../pytorch-unet/INSAT3D_TIR1_India/" 
    
    files=[]
    files_name=[]
    for i in range(len(files_reg_list)):
        img = np.array(Image.open(os.path.join(dir_path,files_reg_list[i]) ))
        files.append(img)
        files_name.append(files_reg_list[i])
        
    files=np.array(files)
    
    mean, std_dev = files.mean(),files.std()
    Max,Min= np.max(files),np.min(files)
    normalised_files=[]
    for img in files:
        if normalization_type=='scaling':
            norm= (img - Min)/(Max-Min)
        if normalization_type=='zscore':
            norm = ((img - mean)/std_dev) 
        normalised_files.append(norm)
        
    files_1      = normalised_files[:34]
    raw_files_1  = files[:34]

    files_name_1 = files_name[:34]

    files_2      = normalised_files[34:]
    raw_files_2  = files[34:]

    files_name_2 = files_name[34:]
    
    
    window_size= inp_seq_len #10
    if normalized_output=='yes':
        output='norm'
    else:
        output='not_norm'
    verify=[]
    tir_x=[]
    tir_y=[]
    for i in range(len(files_1)):
        if (i+window_size+pred_frame-1)>(len(files_1)-1):
            break
        x=files_1[i:i+window_size]
        path=files_name_1[i:i+window_size+pred_frame]
        if output=='norm':
            y=files_1[i+window_size:i+window_size+pred_frame]
        else:
            y=raw_files_1[i+window_size:i+window_size+pred_frame]
        
        verify.append(path)
        tir_x.append(x)
        tir_y.append(y)

    #tir_x,tir_y
    for i in range(len(files_2)):
        if (i+window_size+pred_frame-1)>(len(files_2)-1):
            break
        x=files_2[i:i+window_size]
        path=files_name_2[i:i+window_size+pred_frame]
        if output=='norm':
            y=files_2[i+window_size:i+window_size+pred_frame]
        else:
            y=raw_files_2[i+window_size:i+window_size+pred_frame]
        
        verify.append(path)    
        tir_x.append(x)
        tir_y.append(y)

    tir_x=np.array(tir_x)
    tir_y=np.array(tir_y)

    tir_x=np.reshape(tir_x, (tir_x.shape[0],tir_x.shape[1],tir_x.shape[2],tir_x.shape[3],1))  
    if pred_frame>1:
        tir_y=np.reshape(tir_y, (tir_y.shape[0],y.shape[1],tir_y.shape[2],tir_y.shape[3],1))  
    else:
        tir_y=np.reshape(tir_y, (tir_y.shape[0],tir_y.shape[2],tir_y.shape[3],1)) 
        

    X= tir_x
    y=tir_y
    if normalization_type=='scaling':
         return(X,y,Max,Min,verify)
    else:
        return(X,y,mean, std_dev,verify)