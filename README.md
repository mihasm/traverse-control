# Traverse Control

A Python-based control system for wind tunnel measurements using the ISEL IMC-S8 motorized traverse mechanism. This software enables automated data collection and processing of wind speed and temperature measurements across configurable measurement planes.

## Features

- **Motor Control**: Full control of ISEL IMC-S8 stepper motor controller via RS232 serial interface
- **Automated Measurements**: Programmatic traversal of measurement planes with configurable step sizes and delays
- **Data Processing**: Comprehensive data analysis including averaging, turbulence calculation, and statistical analysis
- **Visualization**: 2D and 3D plotting of measurement results with interpolation
- **Wind Field Interpolation**: Mathematical approximation of wind fields for predictive modeling
- **Real-time Monitoring**: Progress tracking and completion notifications

## Hardware Requirements

- ISEL IMC-S8 motor controller
- RS232 serial connection (USB-to-RS232 adapter recommended)
- Stepper motors for X, Y, Z axes (traverse system)
- Anemometer for wind speed measurements (data logging to XLS files)
- Temperature sensor (integrated with anemometer)

## Software Requirements

- Python 3.6+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mihasm/traverse-control.git
   cd traverse-control
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Connect your ISEL IMC-S8 controller via RS232 serial cable.

## Quick Start

### Basic Motor Control

```python
from commands import Traverse

# Initialize connection (adjust port as needed)
traverse = Traverse(port='COM9')  # Windows
# traverse = Traverse(port='/dev/ttyUSB0')  # Linux

# Initialize the controller for 3-axis operation
traverse.initialize(num_axes=3)

# Get version information
traverse.get_version_data()

# Perform reference run (return to origin)
traverse.reference_run()

# Move to absolute position (500mm, 500mm, 500mm)
traverse.execute_absolute_movement(500, 500, 500)

# Get current position
traverse.get_position()
```

### Automated Plane Traversal

```python
# Traverse a plane (e.g., YZ plane at X=0)
traverse.traverse_plane(
    x1=0, y1=0, x2=0, y2=1000,  # Start and end coordinates
    st_x=1, st_y=10,             # Steps in each direction
    delay=5,                     # Delay at each point (seconds)
    plane="yz"                   # Plane to traverse
)
```

### Data Processing

```python
import procesiranje

# Process measurement data from a specific folder
points_dict = procesiranje.correlate_data(
    traverse_locations="path/to/casi_file",
    MAPA_MERITVE="path/to/measurements"
)

# Generate visualization plots
procesiranje.izrisi_tocke(points_dict, "path/to/casi_file", "path/to/measurements")
```

## Measurement Workflow

1. **Setup**: Connect and initialize the traverse system
2. **Calibration**: Perform reference run to establish coordinate system
3. **Measurement**: Execute automated plane traversal with anemometer logging
4. **Processing**: Correlate timestamped position and measurement data
5. **Analysis**: Calculate averages, turbulence, and generate visualizations
6. **Interpolation**: Create mathematical models of wind fields

## API Reference

### Traverse Class

#### Initialization
- `Traverse(port='COM9')`: Create traverse controller instance

#### Basic Operations
- `initialize(num_axes=3)`: Initialize controller for specified number of axes
- `get_version_data()`: Get controller firmware version
- `reference_run()`: Return traverse to origin position
- `get_position()`: Get current position in millimeters

#### Movement
- `execute_absolute_movement(x, y, z, speed_xyz=(10000,10000,10000))`: Move to absolute coordinates
- `traverse_plane(x1, y1, x2, y2, st_x, st_y, delay=10, plane="zy")`: Automated plane traversal

#### Error Handling
- `error_check_response(response)`: Check controller response for errors

### Data Processing Functions

#### Core Processing
- `correlate_data(traverse_locations, MAPA_MERITVE)`: Correlate position and measurement data
- `calculate_averages(points_dict)`: Compute statistical averages and turbulence

#### Visualization
- `izrisi_tocke(points_dict, traverse_locations, MAPA_MERITVE)`: Generate measurement plots
- `draw_to_matplotlib(x, y, z, ...)`: Create matplotlib visualizations

### Wind Interpolation

#### Approximation
- `create_approximation_plane(x, y, z, order=1)`: Create polynomial approximation of measurement plane
- `get_approximation_planes(order=1)`: Generate approximations for all measurement points

#### Prediction
- `generate_wind(percentage_wind_tunnel, temperature)`: Predict wind speeds
- `get_percentage(temperature, desired_speed)`: Calculate required tunnel speed

## Configuration

### Serial Connection
- Baud rate: 19200
- Data bits: 8
- Stop bits: 1
- Parity: None
- Flow control: None

### Coordinate System
- Maximum range: 1000mm × 1000mm × 1000mm
- Resolution: 0.32mm per step (320 steps = 1mm)
- Reference speeds: 1000 (slow), 5000 (normal), 10000 (fast)

### Measurement Parameters
- Supported planes: xy, yx, xz, zx, yz, zy
- Data format: XLS files from anemometer
- Time synchronization: Automatic timestamp correlation

## Troubleshooting

### Serial Connection Issues
- Verify correct COM port assignment
- Check RS232 cable connections
- Ensure proper power to controller
- Test with different baud rates if needed

### Motor Movement Problems
- Perform reference run after errors
- Check end switch status
- Verify coordinate bounds (0-1000mm)
- Reduce speed if motors stall

### Data Processing Issues
- Ensure XLS files follow expected format
- Check timestamp synchronization
- Verify coordinate system alignment
- Confirm measurement plane configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Miha Smrekar

## Acknowledgments

- ISEL GmbH for the IMC-S8 controller documentation
- Dantec Dynamics for anemometer integration specifications
