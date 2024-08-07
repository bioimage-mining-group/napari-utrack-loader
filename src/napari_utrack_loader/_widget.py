
from typing import TYPE_CHECKING
from magicgui.widgets import Container, create_widget, EmptyWidget
import os
import tifffile
import numpy as np
import json
from napari.utils import progress
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
from time import time
from tqdm.contrib.concurrent import process_map
from functools import partial
import os

if TYPE_CHECKING:
    import napari


# if we want even more control over our widget, we can use
# magicgui `Container`
class UtrackLoader(Container):
    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self._viewer = viewer
        # use create_widget to generate widgets from type annotations
        self._image_folder_path = create_widget(
            widget_type="FileEdit", label="Image Folder",
            options={'mode':'d'}
        )

        self._normalize_checkbox = create_widget(
            widget_type="CheckBox", label="Normalize with percentiles",
        )

        self._median_filter_checkbox = create_widget(
            widget_type="CheckBox", label="Filter size:",
        )

        self._filter_size = create_widget(
            widget_type="SpinBox", label="Filter size",
            options={'value':3, 'min':1, 'max':20, 'step':1}
        )

        self._filter_container = Container(
            widgets=[
                self._median_filter_checkbox,
                self._filter_size,
            ],
            layout='horizontal',
            labels=False,
            label='Apply median filter'
        )

        self._detections_file_path = create_widget(
            widget_type="FileEdit", label="Detections Json File",
            options={'mode':'rm', 'filter':'*.json'} # mode 'rm' means several files
        )

        self._track_file_path = create_widget(
            widget_type="FileEdit", label="Tracks Json File",
            options={'mode':'rm', 'filter':'*.json'} # mode 'rm' means several files
        )

        self._load_button = create_widget(
            widget_type="PushButton", label="Load",
        )

        self._load_button.changed.connect(self._load)

        # append into/extend the container with your widgets
        self.extend(
            [
                self._image_folder_path,
                self._normalize_checkbox,
                self._filter_container,
                self._detections_file_path,
                self._track_file_path,
                EmptyWidget(),
                self._load_button,
            ]
        )

    def _load(self):
        image_path = self._process_path_value(self._image_folder_path)
        detections_path = self._process_path_value(self._detections_file_path)
        track_path = self._process_path_value(self._track_file_path)

        print('image path:', image_path)
        print('detections path:', detections_path)
        print('track path:', track_path)
        
        self._viewer.window._status_bar._toggle_activity_dock(True)
        if len(image_path) > 0:
            self._load_image(image_path)

        self._viewer.window._status_bar._toggle_activity_dock(True)
        if len(detections_path) > 0:
            self._load_detections(detections_path)

        self._viewer.window._status_bar._toggle_activity_dock(True)
        if len(track_path) > 0:
            self._load_tracks(track_path)
        
        self._viewer.window._status_bar._toggle_activity_dock(False)
            

    def _process_path_value(self, path):
        path_value = path.value

        if not isinstance(path_value, tuple):
            path_value = (path_value,)

        paths = [str(value) for value in path_value]
        paths = [
            path
            if (path != '.' and path != '' and os.path.exists(path)) else None
            for path in paths
        ]

        return [path for path in paths if path is not None]
    
    def _normalize(self, image, use_percentiles):
        if use_percentiles:
            # perc_min, perc_max = np.percentile(image, (0.1, 99.9), axis=(1, 2))
            # image = (image - perc_min[:, None, None]) / (perc_max - perc_min)[:, None, None]

            perc_min, perc_max = np.percentile(image, (0.1, 99.9))
            image = (image - perc_min) / (perc_max - perc_min)
        else:
            image = (image - np.min(image)) / (np.max(image) - np.min(image))
        return np.clip(image, 0, 1)
    
    def _apply_median_filter(self, image, size):
        t0 = time()
        func = partial(median_filter, size=size)
        # chunksize = int(image.shape[0] / (4*os.cpu_count()))
        chunksize = 1
        image = np.array(
            process_map(
                func, image, 
                max_workers=os.cpu_count(), chunksize=chunksize, 
                desc='Applying median filter'
            )
        )
        print(f'Median filter applied in {time()-t0:.2f} s')
        return image

    def _load_image(self, paths):
        image_layers = []

        for path in paths:
            if path is None or path == '.':
                continue
            files = os.listdir(path)
            files = [f for f in files if f.endswith('.tif')]
            files.sort()

            image = np.array(
                [
                    tifffile.imread(
                        os.path.join(path, f)
                    ) for f in progress(files, desc='Loading images')
                ]
            )

            image = self._normalize(image, use_percentiles=self._normalize_checkbox.value)

            if self._median_filter_checkbox.value:
                image = self._apply_median_filter(image, size=self._filter_size.value)

            image_layer = self._viewer.add_image(
                image, 
                name=f'{os.path.basename(path)}',
            )

            image_layers.append(image_layer)

        self._image_layers = image_layers

    def _format_path_for_layer_name(self, path):
        return os.path.basename(path).split('.')[0]

    def _load_detections(self, paths):

        detections_layers = []

        for path in paths:

            with open(path, 'r') as f:
                detections = json.load(f)

                if len(detections) == 0:
                    print('No detections found')
                    return
                
                ndim = 3 if len(detections[0]['zCoord']) > 0 else 2
                
                nframes = len(detections)
                npoints = sum([len(d['xCoord']) for d in detections])

                points_data = np.zeros((npoints, 1 + 2*ndim), dtype=np.float32)

                i_detections = 0

                for frame_index, detections_at_t in enumerate(progress(detections, total=nframes, desc='Loading detections')):
                    ndetections = len(detections_at_t['xCoord'])

                    slice_data = slice(
                        i_detections, i_detections+ndetections
                    )
                    
                    if ndim == 3:
                        points_data[slice_data, [1, 2]] = np.array(detections_at_t['zCoord'])
                        points_data[slice_data, [3, 4]] = np.array(detections_at_t['yCoord'])
                        points_data[slice_data, [5, 6]] = np.array(detections_at_t['xCoord'])
                    else:
                        points_data[slice_data, [1, 2]] = np.array(detections_at_t['yCoord'])
                        points_data[slice_data, [3, 4]] = np.array(detections_at_t['xCoord'])

                    points_data[slice_data, 0] = frame_index

                    i_detections += ndetections

                
                sizes = points_data[:, 2::2]
                points_data = points_data[:, [0]+list(range(1, 2*ndim+1, 2))]

                # TODO: implement ellipses
                sizes = np.mean(sizes, axis=1)

                layer_name = self._format_path_for_layer_name(path)
                points_layer = self._viewer.add_points(
                    points_data, 
                    # size=sizes,
                    edge_color='orange',
                    face_color='transparent',
                    name=layer_name,
                )

                detections_layers.append(points_layer)

        self._detections_layers = detections_layers

    def _handle_nones_in_track_object(self, track_object, ndim):

        if ndim == 3:
            track_object_coords = np.array([
                track_object['t'],
                track_object['z'],
                track_object['y'],
                track_object['x']
            ]).T.reshape((-1, 4))
        else:
            track_object_coords = np.array([
                track_object['t'],
                track_object['y'],
                track_object['x']
            ]).T.reshape((-1, 3))

        mask = np.any(track_object_coords == None, axis=1)

        return track_object_coords[~mask]
    
    def _format_coords(self, track_object_coords, utrack_rescale: tuple, scale: tuple, json_format: str):

        if json_format == 'zyx':
            pass # standard parameter

        if json_format == 'xyz':
            track_object_coords = track_object_coords[[0, 2, 1, 3]]
        elif json_format == 'xzy':
            track_object_coords = track_object_coords[[0, 2, 3, 1]]

        utrack_rescale = np.array(utrack_rescale).reshape((-1,1))
        scale = np.array(scale).reshape((-1,1))

        track_object_coords = track_object_coords * utrack_rescale * scale

        return track_object_coords

    def _vec_translate(self, array, dict):
        return np.vectorize(dict.__getitem__)(array)

    def _random_id_property(self, napari_tracks):

        tracks_ids = napari_tracks[:,0]
        unique_tracks_ids = np.unique(tracks_ids)
        shuffled_ids = np.random.permutation(unique_tracks_ids)
        id_dict = {t_id: shuffled_id for t_id, shuffled_id in zip(unique_tracks_ids, shuffled_ids)}

        return self._vec_translate(tracks_ids, id_dict)

    def _load_tracks(self, paths):

        tracks_layers = []

        for path in paths:
            with open(path, 'r') as json_file:
                track_objects = json.load(json_file)

                if not isinstance(track_objects, list):
                    track_objects = [track_objects]

                if len(track_objects) == 0:
                    print('No tracks found')
                    return
                
                ndim = 2 if np.all(np.array(track_objects[0]['z']) == 0) else 3
                nvertices = sum([track_object['numFrames'] for track_object in track_objects])
                
                napari_tracks = np.zeros((nvertices, 2 + ndim), dtype=np.float32)

                i_tracks = 0

                for track_id, track_object in enumerate(progress(track_objects, desc='Loading tracks'), start=1):

                    # if a None appears in one of the coords, the timepoint
                    # is completely removed
                    track_object_coords = self._handle_nones_in_track_object(track_object, ndim)
                    nframes_object = track_object_coords.shape[0]

                    napari_tracks[i_tracks:i_tracks+nframes_object, 1:] = track_object_coords
                    napari_tracks[i_tracks:i_tracks+nframes_object, 0] = track_id

                    i_tracks += nframes_object

                layer_name = os.path.basename(path)[:-5]
                tracks_layer = self._viewer.add_tracks(
                    napari_tracks,
                    name=layer_name,
                    blending='translucent',
                    properties={
                        'random_id': self._random_id_property(napari_tracks)
                    }
                )

                tracks_layer.color_by = 'random_id'

                self._add_tracks_clicking_behaviour(tracks_layer)

                tracks_layers.append(tracks_layer)

        self._tracks_layers = tracks_layers



    def _add_tracks_clicking_behaviour(self, tracks_layer):

        self._fig = None
        self._ax = None

        @tracks_layer.mouse_double_click_callbacks.append
        def on_double_click(layer, event):
            cursor_position = event.position
            track_id = tracks_layer.get_value(cursor_position)
            if track_id is None or len(self._image_layers) == 0:
                return
            print(f'Track id: {track_id}')

            track_data = tracks_layer.data
            track_data = track_data[track_data[:,0] == track_id][:, 1:]

            indices = track_data.round().astype(int)
            frame_indices = indices[:,0]

            if self._fig is None or not plt.fignum_exists(self._fig.number):            
                fig, ax = plt.subplots(1, 1)
                self._fig = fig
                self._ax = ax
                ax.set_xlabel('Frame index')
                ax.set_ylabel('Intensity')

            for layer in self._viewer.layers:
                if layer.__class__.__name__ == 'Image':
                    data = layer.data[tuple(indices.T)]

                    self._ax.plot(frame_indices, data, '-o', 
                                label=f'{layer.name}, id: {track_id}')

            self._ax.legend()
            self._fig.canvas.draw()
            self._fig.show()




            

if __name__ == "__main__":
    import napari
    viewer = napari.Viewer()
    widget = UtrackLoader(viewer)
    viewer.window.add_dock_widget(widget, area='right')

    napari.run()

