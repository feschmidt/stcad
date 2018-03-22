import numpy as np

# Code copied from Lucas H. Gabrielli's heitzmann/gdspy module
# https://github.com/heitzmann/gdspy

def fillet(points,
               radius,
               points_per_2pi=128,
               max_points=199,
               precision=1e-3):
        """
        Round the corners of this polygon and fractures it into polygons with
        less vertices if necessary.

        Parameters
        ----------
        radius : number, list
            Radius of the corners.
        points_per_2pi : integer
            Number of vertices used to approximate a full circle.  The number
            of vertices in each corner of the polygon will be the fraction of
            this number corresponding to the angle encompassed by that corner
            with respect to 2 pi.
        max_points : integer
            Maximal number of points in each resulting polygon (must be greater
            than 4).
        precision : float
            Desired precision for rounding vertice coordinates.

        Returns
        -------
        out : ``Polygon`` or ``PolygonSet``
            If no fracturing occurs, return this object; otherwise return a
            ``PolygonSet`` with the fractured result (this object will have
            more than ``max_points`` vertices).
        """
        points = np.asarray(points)
        two_pi = 2 * np.pi
        vec = points.astype(float) - np.roll(points, 1, 0)
        length = np.sqrt(np.sum(vec**2, 1))
        ii = np.flatnonzero(length)
        if len(ii) < len(length):
            points = points[ii]
            vec = points - np.roll(points, 1, 0)
            length = np.sqrt(np.sum(vec**2, 1))
        vec[:, 0] = vec[:, 0] / length
        vec[:, 1] = vec[:, 1] / length
        dvec = np.roll(vec, -1, 0) - vec
        norm = np.sqrt(np.sum(dvec**2, 1))
        ii = np.flatnonzero(norm)
        dvec[ii, 0] = dvec[ii, 0] / norm[ii]
        dvec[ii, 1] = dvec[ii, 1] / norm[ii]
        theta = np.arccos(np.sum(np.roll(vec, -1, 0) * vec, 1))
        ct = np.cos(theta * 0.5)
        tt = np.tan(theta * 0.5)
        if not isinstance(radius, list):
            radius = [radius] * len(points)
        if not len(points) == len(radius):
            raise ValueError("[GDSPY] Fillet radius list length does not "
                             "match the number of points in the polygon.")

        new_points = []
        for ii in range(-1, len(points) - 1):
            if (theta[ii] > 0) and (radius[ii] > 0):
                a0 = -vec[ii] * tt[ii] - dvec[ii] / ct[ii]
                a0 = np.arctan2(a0[1], a0[0])
                a1 = vec[ii + 1] * tt[ii] - dvec[ii] / ct[ii]
                a1 = np.arctan2(a1[1], a1[0])
                if a1 - a0 > np.pi:
                    a1 -= two_pi
                elif a1 - a0 < -np.pi:
                    a1 += two_pi
                n = max(
                    int(
                        np.ceil(abs(a1 - a0) / two_pi * points_per_2pi) +
                        0.5), 2)
                a = np.linspace(a0, a1, n)
                l = radius[ii] * tt[ii]
                if l > 0.49 * length[ii]:
                    r = 0.49 * length[ii] / tt[ii]
                    l = 0.49 * length[ii]
                else:
                    r = radius[ii]
                if l > 0.49 * length[ii + 1]:
                    r = 0.49 * length[ii + 1] / tt[ii]
                new_points += list(
                    r * dvec[ii] / ct[ii] + points[ii] + np.vstack(
                        (r * np.cos(a), r * np.sin(a))).transpose())
            else:
                new_points.append(points[ii])

        points = np.array(new_points)
        if len(points) > max_points:
            #return fracture(max_points, precision)
            print('Error: max points reached')
        else:
            return points