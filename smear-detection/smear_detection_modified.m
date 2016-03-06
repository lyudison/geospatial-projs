% detect smear area on the lens, and output a mark indicating 
% the area of smear. 

%%%%%%
%Part I%%
%%%%%%

% Edge detection!

% basic idea:
% 1. The big blur is almost the same color, so it is detectable using the
% edge detection method of Matlab.
% 2. Using the erode and dilate to erease the minor edge.
%%%%%%%%%%%%%%%%%%
%%%%%% CODE %%%%%%
%%%%%%%%%%%%%%%%%%

% read names of images

Img = rgb2gray(imread('sample_drive\cam_3\393408606.jpg')); % edge detection is for  a single picture, so any picture is fine

[junk threshold] = edge(Img, 'sobel'); % uisng sobel to detect the edge
fudgeFactor = 0.2;
Edges = edge(Img,'sobel', threshold * fudgeFactor);
figure(1), imshow(Edges), title('binary gradient mask');

se90 = strel('line', 12.5, 90);
se0 = strel('line', 12.5, 0);

BWldil = imdilate(Edges, [se90 se0],2);
figure(2), imshow(BWldil), title('line Dilate');

BWhfill = imfill(BWldil, 'holes');
figure(3), imshow(BWhfill), title('filed the holes');

BWhfill=imcomplement(BWhfill);

seD = strel('diamond',1);
BWfinal = imerode(BWhfill,seD);
BWfinal = imerode(BWfinal,seD);
figure(4), imshow(BWfinal), title('segmented image');

%%%%%%
%Part II%%
%%%%%%

% Series Picture subtract!

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
final= imadd(dil,BWfinal);

% display the processed images
figure(5), imshow(prevImg), title('original image');
figure(6), imshow(accImg), title('accumulated image');
figure(7), imshow(bin), title('binary image');
figure(8), imshow(ero), title('eroded image');
figure(9), imshow(dil), title('dilated image');
figure(10),imshow(final),title('Final');

