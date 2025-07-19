import React from 'react';
import { Thermometer, Droplets } from 'lucide-react';
import { Badge } from './ui/badge';

interface SquirrelBoxSensorsProps {
  temperature: number;
  humidity: number;
  lastUpdate: string;
}

export function SquirrelBoxSensors({ temperature, humidity, lastUpdate }: SquirrelBoxSensorsProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex items-center gap-4 flex-wrap">
      <Badge variant="secondary" className="sensor-badge flex items-center gap-1">
        <Thermometer className="h-3 w-3" />
        {temperature}°F
      </Badge>
      <Badge variant="secondary" className="sensor-badge flex items-center gap-1">
        <Droplets className="h-3 w-3" />
        {humidity}%
      </Badge>
      <span className="text-xs text-stone-500">
        Updated {formatTime(lastUpdate)}
      </span>
    </div>
  );
}
