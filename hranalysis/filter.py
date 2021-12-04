import numpy as np
from sklearn.linear_model import LinearRegression


def threshold_filter(hr_array, intervals_array=None, threshold=10):
    """
    Filters heart rate using a variation threshold and linear regression
    
    Parameters
    ----------
        
    hr_array: np.array
        Array of heart rate values.
        
    intervals_array: np.array (optional, default None)
        Array of exercise intervals.
      
    threshold: int (optional, default 10)
        The amount of variation allowed between heart rate samples.
    
    Return
    -----------
    return: np.array
        Returns the filtered heart rate.
    """
    
    filtered = np.empty(len(hr_array))
    
    if intervals_array is None:
        intervals_array = np.array([1]*len(hr_array))
        
    for interval_num in np.unique(intervals_array):
        idx = np.where(intervals_array == interval_num)[0]
        interval_hr = hr_array[idx]
        
        threshold_condition = np.abs(np.diff(interval_hr, prepend = interval_hr[0])) > threshold
        positive_condition = interval_hr == 0
        outliers = np.where(np.logical_or(threshold_condition, positive_condition))[0]

        if len(outliers) > 1:
            split_distance = 5
            split_idxs = np.where((np.diff(outliers, prepend=outliers[0]) > split_distance))[0]
            clusters = np.split(outliers, split_idxs)

            for cluster in clusters:
                if len(cluster)>1:
                    window = np.arange(cluster[0], cluster[-1]+1)
                    X = np.delete(np.arange(len(interval_hr)), window).reshape(-1, 1)
                    if len(X) == 0:
                        y_pred = interval_hr
                    else:
                        y = np.delete(interval_hr, window)

                        linear_regressor = LinearRegression()
                        linear_regressor.fit(X, y)
                        y_pred = linear_regressor.predict(window.reshape(-1,1))

                        interval_hr[window] = y_pred

        filtered[idx] = interval_hr
    
    return filtered