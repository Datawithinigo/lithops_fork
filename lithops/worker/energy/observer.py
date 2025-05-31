#
# (C) Copyright IBM Corp. 2020
# (C) Copyright Cloudlab URV 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from abc import ABC, abstractmethod
from typing import Dict, Any, List

class EnergyObserver(ABC):
    """
    Observer interface for energy monitoring events.
    Implements the Observer pattern to allow components to be notified
    of energy monitoring events.
    """
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Update the observer with new energy monitoring data.
        
        Args:
            event_type: The type of event (e.g., 'start', 'stop', 'data').
            data: The event data.
        """
        pass


class EnergySubject:
    """
    Subject interface for the Observer pattern.
    Energy monitors can implement this to notify observers of events.
    """
    
    def __init__(self):
        self._observers: List[EnergyObserver] = []
    
    def attach(self, observer: EnergyObserver) -> None:
        """
        Attach an observer to this subject.
        
        Args:
            observer: The observer to attach.
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: EnergyObserver) -> None:
        """
        Detach an observer from this subject.
        
        Args:
            observer: The observer to detach.
        """
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
    
    def notify(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Notify all observers of an event.
        
        Args:
            event_type: The type of event.
            data: The event data.
        """
        for observer in self._observers:
            observer.update(event_type, data)
