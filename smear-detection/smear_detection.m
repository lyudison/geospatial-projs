% detect smear area on the lens, and output a mask indicating 
% the area of smear. 

% basic idea:
% 1. subtract each image with its next image
% 2. accumulate the `different area' 
% 3. binarize and negate the `accumulated image'
% 4. erode and dilate the image to emphasize the smear

% challenges:
% 1. how to preprocess to gain ideal images
% 2. when to stop accumulating subtracted images

%%%%%%%%%%%%%%%%%%
%%%%%% CODE %%%%%%
%%%%%%%%%%%%%%%%%%

% read names of images
imgFolder = 'sample_drive/cam_3/';
imgNames = dir(imgFolder);
n = size(imgNames, 1);

% read image size to create an empty image for storing accumulation
imgName = imgNames(4).name;
prevImg = rgb2gray(imread(strcat(imgFolder, imgName)));
accImg = uint8(zeros(size(prevImg, 1), size(prevImg, 2), 1));

% subtract each image with its previous image
for i = 5: floor(n/20): n % skip the first 3 invalid file names and the first image
    imgName = imgNames(i).name;
    img = rgb2gray(imread(strcat(imgFolder, imgName)));
    sub = imsubtract(img, prevImg);
    accImg = imadd(accImg, sub);
    prevImg = img;
end

% negate
neg = imcomplement(accImg);

% binarize
bin = im2bw(neg, 0.3);

% erode
SE = strel('disk', 8);
ero = imerode(bin, SE);

% dilate
dil = imdilate(ero, SE);

% display the processed images
subplot(1, 5, 1), imshow(prevImg), title('original image');
subplot(1, 5, 2), imshow(accImg), title('accumulated image');
subplot(1, 5, 3), imshow(bin), title('binary image');
subplot(1, 5, 4), imshow(ero), title('eroded image');
subplot(1, 5, 5), imshow(dil), title('dilated image');
