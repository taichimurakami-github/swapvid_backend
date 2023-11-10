# Backend alpha system development

## Domains

### Converter

To convert any data

- Pdf -> Img : pdf2img
- Img -> Text : img2string
- Ocr linebased fmt -> Matchable fmt : img2string

### Matcher

To match different data

- Text <-> Text (from video frame ,and from document pdf)

### Analyzer

To analyze and get infomation from data

- Basic image analysis: class ImageAnalyzer
- Basic video frame analysis: class VideoFrameDetector extends ImageAnalyzer
- Analyze video activities : class VideoActivityAnalyzer extends VideoFrameDetector

## Sequence between UI thread and Backend thread

### Matching sequence

```mermaid
sequenceDiagram
  participant u as UI_Thread
  participant b as BK_Thread

  loop Every seconds
    Note over u: 1.canvas.toDataURL(video)
    Note over u: 2.fetch(post, bodu=dataURL)
    u ->>+ b: POST
    Note over u,b: "{body: <<encoded dataURL>>}"
    Note over b: 1.Convert dataURL to Image<br/>(openCV.Mat, pil.Image)
    Note over b: 2.Perform frame-diff analysis
    alt no frame diff detected
        b ->> u: (res)
        Note over b,u : httpStatus: 200
    else no frame diff detected
      Note over b: 3.Perform OCR
      Note over b: 4.Perform text-basaed matching
      alt match succeeded
        b ->> u: (res)
        Note over b,u : httpStatus: 200,<br/>'body: application/json'<br/>{media_meta:[w,h,fps,fcnt],<br/>match_result:<br/>{content: str,<br/>linePosition: [t,l,b,r]}[]<br/>}
      else match failed
        b ->>- u: (res)
        Note over b,u : httpStatus: 200
      end
    end

  end

```
